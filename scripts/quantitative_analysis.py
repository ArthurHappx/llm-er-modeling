#!/usr/bin/env python3
"""Reproducible quantitative analysis for the LLM ER-modeling experiment."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


DIMENSIONS = [
    "Completeness", "Correctness", "Clarity",
    "Simplicity", "Flexibility", "Implementability",
]
PROMPT_ORDER = ["One-shot", "CoT", "CoT + Verifier"]
MODEL_ORDER = ["GPT-5.1", "Qwen-3"]
SECTION_RE = re.compile(r"^###\s+(?:\d+(?:\.\d+)*\.?\s*)?(.+?)\s*$")
ITEM_RE = re.compile(r"^\s*-\s*\[([xX ])\]\s*(.+?)\s*$")
METADATA_RE = re.compile(r"`\s*(llm|prompt|scenario)\s*:\s*([^`]+?)\s*`", re.IGNORECASE)

ENTITY_ALIASES = {
    "personnel": "person", "people": "person",
    "hospital_department": "department",
    "resident_physician": "resident",
    "admin_staff": "administrative_staff",
    "employee_dependent": "dependent",
    "department_coordinator": "department_responsibility",
    "department_coordinator_assignment": "department_responsibility",
    "department_shift_leader": "department_responsibility",
    "department_shift_responsibility": "department_responsibility",
    "shift_responsibility": "department_responsibility",
    "employee_contract": "employment_contract",
    "employee_hospital_contract": "employment_contract",
    "contract": "employment_contract",
    "schedule": "work_schedule", "employee_schedule": "work_schedule",
    "work_shift": "work_schedule",
    "time_clock": "time_record", "time_clock_record": "time_record",
    "patient_department_movement": "patient_movement",
    "person_card_assignment": "card_assignment",
    "temporary_card_usage": "card_assignment",
    "card_history": "card_status_history",
    "lost_card_report": "card_loss_event",
    "defective_card": "card_failure_event",
    "manual_validation": "manual_access_validation",
    "access_log": "access_event", "access_history": "access_event",
    "card_access_attempt": "access_event", "visitor_access": "access_event",
    "visitor_visit": "access_event",
    "department_capacity_alert": "department_occupancy",
    "department_occupancy_alert": "department_occupancy",
    "department_occupancy_snapshot": "department_occupancy",
    "patient_isolation": "patient_isolation", "isolation_note": "patient_isolation",
    "patient_admission": "patient_visit",
    "companion_authorization": "companion_authorization",
    "visitor_access_authorization": "companion_authorization",
    "researcher_role": "researcher", "physician_researcher": "researcher",
    "nurse_researcher": "researcher",
}

ATTRIBUTE_ALIASES = {
    "identifier": "id", "personnel_id": "person_id", "person_id_fk": "person_id",
    "date_of_birth": "birth_date", "dob": "birth_date",
    "last_update_ts": "last_updated", "last_updated_at": "last_updated",
    "updated_at": "last_updated", "timestamp_last_update": "last_updated",
    "zip_code": "postal_code", "cep": "postal_code",
    "card_type": "type", "visitor_type": "type", "exception_type": "type",
    "contract_type": "type", "movement_type": "type",
    "active_status": "active", "is_active": "active",
    "full_name": "full_name", "name_full": "full_name",
    "date_time": "timestamp", "event_ts": "timestamp", "movement_date": "timestamp",
    "clock_in_ts": "clock_in", "clock_out_ts": "clock_out",
    "start_date_time": "start", "end_date_time": "end",
    "start_datetime": "start", "end_datetime": "end",
}


def snake(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return value


def canon_entity(value: str) -> str:
    name = snake(value)
    return ENTITY_ALIASES.get(name, name)


def canon_attribute(value: str) -> str:
    name = snake(value.lstrip("*+"))
    name = re.sub(r"^(pk|fk)_", "", name)
    return ATTRIBUTE_ALIASES.get(name, name)


def labels_from_path(path: Path) -> tuple[str, str, str]:
    folder_model = path.parts[-3].lower()
    model = "GPT-5.1" if folder_model.startswith("gpt") else "Qwen-3"
    prompts = {"one-shot": "One-shot", "cot": "CoT", "cot-verifier": "CoT + Verifier"}
    prompt = prompts[path.stem.lower()]
    scenario = path.parts[-2].replace("scenario_", "")
    return model, prompt, scenario


def parse_checklists(analysis_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    score_rows, item_rows = [], []
    for path in sorted(analysis_dir.glob("*/*/*.md")):
        model, prompt, scenario = labels_from_path(path)
        current = None
        values: dict[str, list[int]] = defaultdict(list)
        for line in path.read_text(encoding="utf-8").splitlines():
            heading = SECTION_RE.match(line)
            if heading:
                title = heading.group(1).strip()
                current = title if title in DIMENSIONS else None
            item = ITEM_RE.match(line)
            if item and current:
                checked = int(item.group(1).lower() == "x")
                text = item.group(2).strip()
                values[current].append(checked)
                item_rows.append({"Model": model, "Prompt": prompt, "Scenario": scenario,
                                  "Dimension": current, "Criterion": text, "Satisfied": checked})
        counts = [len(values[d]) for d in DIMENSIONS]
        if counts != [5, 6, 5, 5, 3, 2]:
            raise ValueError(f"Unexpected checklist structure in {path}: {counts}")
        dims = {d: 100 * sum(values[d]) / len(values[d]) for d in DIMENSIONS}
        total = sum(counts)
        row = {"Model": model, "Prompt": prompt, "Scenario": scenario,
               "CQS": 100 * sum(sum(values[d]) for d in DIMENSIONS) / total,
               "Macro CQS": np.mean(list(dims.values())), **dims}
        score_rows.append(row)
    scores = pd.DataFrame(score_rows)
    if len(scores) != 18:
        raise ValueError(f"Expected 18 checklists, found {len(scores)}")
    return scores, pd.DataFrame(item_rows)


def audit_metadata(analysis_dir: Path) -> pd.DataFrame:
    rows = []
    model_map = {"gpt": "GPT-5.1", "gpt-5.1": "GPT-5.1", "qwen": "Qwen-3", "qwen-3": "Qwen-3"}
    prompt_map = {"zero": "One-shot", "one-shot": "One-shot", "cot": "CoT",
                  "pos-verifier": "CoT + Verifier", "cot-verifier": "CoT + Verifier"}
    for path in sorted(analysis_dir.glob("*/*/*.md")):
        expected_model, expected_prompt, expected_scenario = labels_from_path(path)
        found = {m.group(1).lower(): m.group(2).strip() for m in METADATA_RE.finditer(path.read_text(encoding="utf-8"))}
        observed_model = model_map.get(found.get("llm", "").lower(), found.get("llm", "<missing>"))
        observed_prompt = prompt_map.get(found.get("prompt", "").lower(), found.get("prompt", "<missing>"))
        observed_scenario = found.get("scenario", "<missing>")
        issues = []
        if observed_model != expected_model: issues.append("model")
        if observed_prompt != expected_prompt: issues.append("prompt")
        if observed_scenario != expected_scenario: issues.append("scenario")
        rows.append({"File": str(path.relative_to(analysis_dir)), "Expected Model": expected_model,
                     "Metadata Model": observed_model, "Expected Prompt": expected_prompt,
                     "Metadata Prompt": observed_prompt, "Expected Scenario": expected_scenario,
                     "Metadata Scenario": observed_scenario, "Issues": ", ".join(issues) or "none"})
    return pd.DataFrame(rows)


def extract_schema(response: str) -> dict | None:
    response = response.strip()
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", response):
        try:
            obj, _ = decoder.raw_decode(response[match.start():])
            if isinstance(obj, dict) and isinstance(obj.get("tables"), dict):
                return obj
        except json.JSONDecodeError:
            continue
    return None


def load_generated_schemas(raw_dir: Path) -> dict[tuple[str, str, str], dict]:
    schemas = {}
    for path in sorted(raw_dir.glob("*/scenario_*/*.json")):
        model, prompt, scenario = labels_from_path(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = payload if isinstance(payload, list) else [payload]
        schema = None
        for entry in reversed(entries):
            schema = extract_schema(str(entry.get("response", "")))
            if schema:
                break
        if not schema:
            raise ValueError(f"Could not extract final schema from {path}")
        schemas[(model, prompt, scenario)] = schema
    if len(schemas) != 18:
        raise ValueError(f"Expected 18 generated schemas, found {len(schemas)}")
    return schemas


def materialize_gold(path: Path) -> dict[str, dict]:
    source = json.loads(path.read_text(encoding="utf-8"))
    entities = {k: list(v) for k, v in source["scenario_01"]["entities"].items()}
    relations = list(source["scenario_01"]["relations"])
    result = {"01": {"entities": json.loads(json.dumps(entities)), "relations": list(relations)}}
    for scenario, delta_name in [("02", "scenario_02_additions"), ("03", "scenario_03_additions")]:
        delta = source[delta_name]
        entities.update({k: list(v) for k, v in delta["entities"].items()})
        for entity, attrs in delta.get("entity_attribute_additions", {}).items():
            entities[entity] = sorted(set(entities[entity]) | set(attrs))
        relations.extend(delta["relations"])
        result[scenario] = {"entities": json.loads(json.dumps(entities)), "relations": list(relations)}
    return result


def schema_features(schema: dict) -> tuple[dict[str, set[str]], set[tuple[str, str]], dict[tuple[str, str], str]]:
    entities: dict[str, set[str]] = defaultdict(set)
    for table, attrs in schema.get("tables", {}).items():
        entity = canon_entity(table)
        if isinstance(attrs, dict):
            entities[entity].update(canon_attribute(a) for a in attrs)
        elif isinstance(attrs, list):
            for item in attrs:
                if isinstance(item, dict):
                    entities[entity].update(canon_attribute(a) for a in item)
    pairs, cards = set(), {}
    for relation in schema.get("relations", []):
        if not isinstance(relation, str):
            continue
        match = re.match(r"\s*([^:\s]+)(?::[^\s]+)?\s+([^\s]+)\s+([^:\s]+)(?::[^\s]+)?", relation)
        if not match:
            continue
        left, card, right = canon_entity(match.group(1)), match.group(2), canon_entity(match.group(3))
        pair = tuple(sorted((left, right)))
        pairs.add(pair)
        cards[pair] = cardinality_class(card)
    return dict(entities), pairs, cards


def gold_features(gold: dict) -> tuple[dict[str, set[str]], set[tuple[str, str]], dict[tuple[str, str], str]]:
    entities = {canon_entity(k): {canon_attribute(a) for a in v} for k, v in gold["entities"].items()}
    pairs, cards = set(), {}
    for left, right, card in gold["relations"]:
        pair = tuple(sorted((canon_entity(left), canon_entity(right))))
        pairs.add(pair)
        cards[pair] = cardinality_class(card)
    return entities, pairs, cards


def cardinality_class(value: str) -> str:
    value = value.lower()
    many = any(char in value for char in ("*", "+", "{")) or "n" in value
    return "one_many" if many else "one_one"


def prf(tp: int, predicted: int, expected: int) -> tuple[float, float, float]:
    precision = tp / predicted if predicted else 0.0
    recall = tp / expected if expected else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def fuzzy_attribute_matches(pred: dict[str, set[str]], gold: dict[str, set[str]]) -> tuple[int, int, int]:
    tp, pred_total, gold_total = 0, sum(map(len, pred.values())), sum(map(len, gold.values()))
    for entity in set(pred) & set(gold):
        remaining = set(gold[entity])
        for attribute in sorted(pred[entity]):
            if attribute in remaining:
                tp += 1; remaining.remove(attribute); continue
            candidates = [(SequenceMatcher(None, attribute, target).ratio(), target) for target in remaining]
            if candidates:
                score, target = max(candidates)
                if score >= 0.67:
                    tp += 1; remaining.remove(target)
    return tp, pred_total, gold_total


def canonical_tokens(entities: dict[str, set[str]], pairs: set[tuple[str, str]]) -> list[str]:
    tokens = []
    for entity in sorted(entities):
        tokens.append(f"entity_{entity}")
        tokens.extend(f"attribute_{entity}_{a}" for a in sorted(entities[entity]))
    tokens.extend(f"relation_{a}_{b}" for a, b in sorted(pairs))
    return tokens


def rouge_l(pred: list[str], gold: list[str]) -> float:
    previous = [0] * (len(gold) + 1)
    for token in pred:
        current = [0]
        for j, target in enumerate(gold, 1):
            current.append(previous[j - 1] + 1 if token == target else max(previous[j], current[-1]))
        previous = current
    lcs = previous[-1]
    p, r, _ = prf(lcs, len(pred), len(gold))
    return 2 * p * r / (p + r) if p + r else 0.0


def bleu4(pred: list[str], gold: list[str]) -> float:
    if not pred:
        return 0.0
    logs = []
    for n in range(1, 5):
        pgrams = [tuple(pred[i:i+n]) for i in range(max(0, len(pred)-n+1))]
        ggrams = [tuple(gold[i:i+n]) for i in range(max(0, len(gold)-n+1))]
        gcounts = defaultdict(int)
        for gram in ggrams: gcounts[gram] += 1
        matched = 0
        seen = defaultdict(int)
        for gram in pgrams:
            if seen[gram] < gcounts[gram]: matched += 1
            seen[gram] += 1
        precision = (matched + 1) / (len(pgrams) + 1)
        logs.append(math.log(precision))
    brevity = 1.0 if len(pred) >= len(gold) else math.exp(1 - len(gold) / len(pred))
    return brevity * math.exp(sum(logs) / 4)


def reference_metrics(schemas: dict, golds: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for (model, prompt, scenario), schema in schemas.items():
        pred_entities, pred_pairs, pred_cards = schema_features(schema)
        gold_entities, gold_pairs, gold_cards = gold_features(golds[scenario])
        ep, er, ef = prf(len(set(pred_entities) & set(gold_entities)), len(pred_entities), len(gold_entities))
        atp, apred, agold = fuzzy_attribute_matches(pred_entities, gold_entities)
        ap, ar, af = prf(atp, apred, agold)
        rp, rr, rf = prf(len(pred_pairs & gold_pairs), len(pred_pairs), len(gold_pairs))
        common = pred_pairs & gold_pairs
        card_acc = np.mean([pred_cards[p] == gold_cards[p] for p in common]) if common else 0.0
        ptokens, gtokens = canonical_tokens(pred_entities, pred_pairs), canonical_tokens(gold_entities, gold_pairs)
        rows.append({
            "Model": model, "Prompt": prompt, "Scenario": scenario,
            "Entity Precision": 100*ep, "Entity Recall": 100*er, "Entity F1": 100*ef,
            "Attribute Precision": 100*ap, "Attribute Recall": 100*ar, "Attribute F1": 100*af,
            "Relation Precision": 100*rp, "Relation Recall": 100*rr, "Relation F1": 100*rf,
            "Cardinality Accuracy": 100*card_acc,
            "Structural F1": 100*np.mean([ef, af, rf]),
            "ROUGE-L": 100*rouge_l(ptokens, gtokens), "BLEU-4": 100*bleu4(ptokens, gtokens),
        })
    return pd.DataFrame(rows)


def design_matrix(scores: pd.DataFrame) -> tuple[np.ndarray, dict[str, list[int]], np.ndarray]:
    model = np.where(scores["Model"].eq("GPT-5.1"), 0.5, -0.5)
    prompt = scores["Prompt"]
    p1 = np.where(prompt.eq("One-shot"), -1.0, np.where(prompt.eq("CoT"), 1.0, 0.0))
    p2 = np.where(prompt.eq("One-shot"), -0.5, np.where(prompt.eq("CoT"), -0.5, 1.0))
    scenarios = pd.get_dummies(scores["Scenario"], drop_first=True, dtype=float).to_numpy()
    cols = [np.ones(len(scores)), *[scenarios[:, i] for i in range(scenarios.shape[1])], model, p1, p2, model*p1, model*p2]
    x = np.column_stack(cols)
    terms = {"Model": [3], "Prompt": [4, 5], "Model x Prompt": [6, 7]}
    return x, terms, scores["Scenario"].to_numpy()


def sse(x: np.ndarray, y: np.ndarray) -> float:
    residual = y - x @ np.linalg.lstsq(x, y, rcond=None)[0]
    return float(residual @ residual)


def permutation_tests(scores: pd.DataFrame, permutations: int = 20000, seed: int = 20260720) -> pd.DataFrame:
    ordered = scores.sort_values(["Scenario", "Model", "Prompt"]).reset_index(drop=True)
    y = ordered["CQS"].to_numpy(float)
    x, terms, blocks = design_matrix(ordered)
    full_sse = sse(x, y); df_error = len(y) - np.linalg.matrix_rank(x)
    rng = np.random.default_rng(seed); rows = []
    for term, indexes in terms.items():
        keep = [i for i in range(x.shape[1]) if i not in indexes]
        reduced = x[:, keep]
        reduced_sse = sse(reduced, y)
        df_term = np.linalg.matrix_rank(x) - np.linalg.matrix_rank(reduced)
        observed = ((reduced_sse - full_sse) / df_term) / (full_sse / df_error)
        beta = np.linalg.lstsq(reduced, y, rcond=None)[0]
        fitted = reduced @ beta; residual = y - fitted
        exceed = 0
        for _ in range(permutations):
            permuted = residual.copy()
            for block in np.unique(blocks):
                idx = np.flatnonzero(blocks == block)
                permuted[idx] = rng.permutation(permuted[idx])
            yp = fitted + permuted
            fs, rs = sse(x, yp), sse(reduced, yp)
            fperm = ((rs - fs) / df_term) / (fs / df_error) if fs > 0 else 0
            exceed += fperm >= observed - 1e-12
        rows.append({"Effect": term, "df": df_term, "F": observed,
                     "Permutation p": (exceed + 1) / (permutations + 1),
                     "Partial eta squared": (reduced_sse-full_sse)/(reduced_sse-full_sse+full_sse)})
    return pd.DataFrame(rows)


def planned_contrasts(scores: pd.DataFrame) -> pd.DataFrame:
    pivot = scores.pivot_table(index=["Scenario", "Prompt"], columns="Model", values="CQS")
    model_diff = pivot["GPT-5.1"] - pivot["Qwen-3"]
    rows = [{"Contrast": "GPT-5.1 - Qwen-3", "Mean difference": model_diff.mean(), "SD difference": model_diff.std(ddof=1)}]
    for left, right in [("CoT", "One-shot"), ("CoT + Verifier", "CoT")]:
        p = scores.pivot_table(index=["Scenario", "Model"], columns="Prompt", values="CQS")
        diff = p[left] - p[right]
        rows.append({"Contrast": f"{left} - {right}", "Mean difference": diff.mean(), "SD difference": diff.std(ddof=1)})
    for row in rows:
        row["Standardized paired effect (dz)"] = row["Mean difference"] / row["SD difference"] if row["SD difference"] else np.nan
    return pd.DataFrame(rows)


def aggregate_tables(scores: pd.DataFrame, refs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    main = scores.groupby(["Model", "Prompt"], sort=False).agg(
        **{d: (d, "mean") for d in DIMENSIONS},
        **{"CQS Mean": ("CQS", "mean"), "CQS SD": ("CQS", "std"), "Macro CQS": ("Macro CQS", "mean")},
    ).reset_index()
    main["Rank"] = main["CQS Mean"].rank(method="min", ascending=False).astype(int)
    main = main.sort_values("Rank")
    reference = refs.groupby(["Model", "Prompt"], sort=False).agg(
        **{name: (name, "mean") for name in ["Entity F1", "Attribute F1", "Relation F1", "Cardinality Accuracy", "Structural F1", "ROUGE-L", "BLEU-4"]}
    ).reset_index()
    return main, reference


def write_latex(df: pd.DataFrame, path: Path, columns: list[str]) -> None:
    view = df[columns].copy()
    for col in view.select_dtypes(include=["number"]).columns:
        view[col] = view[col].map(lambda x: f"{x:.2f}")
    def escape(value: object) -> str:
        text = str(value)
        for source, target in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                               ("_", r"\_"), ("#", r"\#"), ("$", r"\$")]:
            text = text.replace(source, target)
        return text
    lines = [r"\begin{tabular}{" + "ll" + "r"*(len(columns)-2) + "}", r"\toprule",
             " & ".join(escape(c) for c in columns) + r" \\", r"\midrule"]
    lines.extend(" & ".join(escape(value) for value in row) + r" \\" for row in view.itertuples(index=False, name=None))
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def heat_color(value: float) -> tuple[int, int, int]:
    anchors = [(0, (255, 255, 217)), (50, (65, 182, 196)), (100, (8, 64, 129))]
    left, right = anchors[0], anchors[-1]
    for index in range(len(anchors) - 1):
        if anchors[index][0] <= value <= anchors[index + 1][0]:
            left, right = anchors[index], anchors[index + 1]; break
    ratio = (value-left[0])/(right[0]-left[0]) if right[0] != left[0] else 0
    return tuple(round(left[1][i] + ratio*(right[1][i]-left[1][i])) for i in range(3))


def heatmap(main: pd.DataFrame, path: Path) -> None:
    labels = (main["Model"] + " / " + main["Prompt"]).tolist()
    matrix = main[DIMENSIONS].to_numpy()
    left, top, cell_w, cell_h = 310, 120, 175, 68
    width, height = left + cell_w*len(DIMENSIONS) + 40, top + cell_h*len(labels) + 75
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas); font = ImageFont.load_default(size=18); small = ImageFont.load_default(size=16)
    title = "Checklist Quality Score by Dimension (%)"
    draw.text((width//2, 30), title, fill="black", font=ImageFont.load_default(size=24), anchor="ma")
    for j, dimension in enumerate(DIMENSIONS):
        draw.text((left+j*cell_w+cell_w//2, top-18), dimension, fill="black", font=small, anchor="ms")
    for i, label in enumerate(labels):
        y = top+i*cell_h
        draw.text((left-18, y+cell_h//2), label, fill="black", font=font, anchor="rm")
        for j, value in enumerate(matrix[i]):
            x = left+j*cell_w; color = heat_color(float(value))
            draw.rectangle((x, y, x+cell_w, y+cell_h), fill=color, outline="white", width=2)
            luminance = sum((0.299, 0.587, 0.114)[k]*color[k] for k in range(3))
            draw.text((x+cell_w//2, y+cell_h//2), f"{value:.1f}",
                      fill="white" if luminance < 130 else "black", font=font, anchor="mm")
    canvas.save(path, dpi=(300, 300))


def markdown_table(df: pd.DataFrame) -> str:
    display = df.copy()
    for column in display.select_dtypes(include=["number"]).columns:
        display[column] = display[column].map(lambda value: f"{value:.2f}")
    headers = [str(column) for column in display.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"]*len(headers)) + " |"]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in display.itertuples(index=False, name=None))
    return "\n".join(lines)


def report_text(main: pd.DataFrame, ref: pd.DataFrame, tests: pd.DataFrame, contrasts: pd.DataFrame) -> str:
    best = main.iloc[0]
    lines = [
        "# Quantitative analysis report", "",
        "The analysis covers 18 outputs (2 models x 3 prompting techniques x 3 scenarios). ",
        "CQS is the percentage of the 26 checklist items marked as satisfied. Dimension scores are calculated within each checklist dimension.", "",
        "## Main CQS table", "", markdown_table(main), "",
        "## Gold-standard comparison", "", markdown_table(ref), "",
        "## Blocked factorial permutation tests", "", markdown_table(tests), "",
        "## Planned descriptive contrasts", "", markdown_table(contrasts), "",
        "## Interpretation", "",
        f"The highest mean CQS was obtained by {best['Model']} with {best['Prompt']} ({best['CQS Mean']:.2f}%, SD={best['CQS SD']:.2f}).",
        "Because each model-prompt combination has only three scenario-level observations, inferential results are exploratory. Effect sizes and scenario-level consistency should be considered together with permutation p-values.",
        "ROUGE-L and BLEU-4 were computed over canonicalized schema-feature sequences and are secondary lexical-overlap measures; structural precision, recall and F1 are more appropriate for semantically equivalent ER designs.",
    ]
    return "\n".join(lines) + "\n"


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "analysis").is_dir() and (candidate / "raw_outputs").is_dir():
            return candidate
    raise FileNotFoundError("Could not locate repository root containing analysis/ and raw_outputs/.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--permutations", type=int, default=20000)
    args = parser.parse_args()
    root = (args.root or find_repo_root(Path(__file__).resolve())).resolve(); out = root / "results_quantitative"
    (out / "figures").mkdir(parents=True, exist_ok=True); (out / "latex").mkdir(exist_ok=True)
    scores, items = parse_checklists(root / "analysis")
    metadata_audit = audit_metadata(root / "analysis")
    schemas = load_generated_schemas(root / "raw_outputs")
    golds = materialize_gold(root / "reference_model" / "gold_standard.json")
    refs = reference_metrics(schemas, golds)
    tests = permutation_tests(scores, args.permutations)
    contrasts = planned_contrasts(scores)
    main_table, reference_table = aggregate_tables(scores, refs)
    scores.round(6).to_csv(out / "checklist_scores.csv", index=False)
    items.to_csv(out / "checklist_item_outcomes.csv", index=False)
    metadata_audit.to_csv(out / "metadata_audit.csv", index=False)
    refs.round(6).to_csv(out / "reference_metrics.csv", index=False)
    main_table.round(4).to_csv(out / "table_cqs_by_model_prompt.csv", index=False)
    reference_table.round(4).to_csv(out / "table_reference_metrics.csv", index=False)
    tests.round(6).to_csv(out / "statistical_tests.csv", index=False)
    contrasts.round(6).to_csv(out / "planned_contrasts.csv", index=False)
    write_latex(main_table, out / "latex" / "table_cqs.tex", ["Model", "Prompt", *DIMENSIONS, "CQS Mean", "CQS SD", "Rank"])
    write_latex(reference_table, out / "latex" / "table_reference_metrics.tex", ["Model", "Prompt", "Entity F1", "Attribute F1", "Relation F1", "Structural F1", "ROUGE-L", "BLEU-4"])
    heatmap(main_table, out / "figures" / "cqs_dimensions_heatmap.png")
    (out / "analysis_report.md").write_text(report_text(main_table, reference_table, tests, contrasts), encoding="utf-8")
    manifest = {"models": MODEL_ORDER, "prompts": PROMPT_ORDER, "scenarios": ["01", "02", "03"],
                "outputs": 18, "checklist_items_per_output": 26, "permutations": args.permutations,
                "model_label_note": "GPT outputs are labeled GPT-5.1. The analysis checklist directory was renamed from gpt-4.1 to gpt-5.1 after confirming the model version."}
    (out / "analysis_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(report_text(main_table, reference_table, tests, contrasts))


if __name__ == "__main__":
    main()
