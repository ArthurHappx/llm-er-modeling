#!/usr/bin/env python3
"""Analyze checklist markdown files and generate quantitative results."""

from __future__ import annotations

import argparse
import logging
import math
import os
import re
import textwrap
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    from scipy import stats
except ImportError:  # pragma: no cover - depends on the local environment.
    stats = None


EXPECTED_SECTIONS = [
    "Completeness",
    "Correctness",
    "Clarity",
    "Simplicity",
    "Flexibility",
    "Implementability",
]

METADATA_RE = re.compile(r"`\s*(llm|prompt|scenario)\s*:\s*([^`]+?)\s*`", re.IGNORECASE)
SECTION_RE = re.compile(r"^###\s+(?:\d+(?:\.\d+)*\.?\s*)?(?P<title>.+?)\s*$")
CHECKLIST_ITEM_RE = re.compile(r"^\s*-\s*\[(?P<mark>[xX\s])\]\s*(?P<text>.+?)\s*$")


@dataclass(frozen=True)
class Criterion:
    section: str
    text: str
    checked: bool


@dataclass(frozen=True)
class ChecklistResult:
    path: Path
    llm: str
    prompt: str
    scenario: str
    sections: tuple[str, ...]
    criteria: tuple[Criterion, ...]
    notes: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse checklist markdown files and generate result tables and figures."
    )
    parser.add_argument("--input", default="analysis/", type=Path, help="Input analysis directory.")
    parser.add_argument("--output", default="results/", type=Path, help="Output results directory.")
    parser.add_argument("--dpi", default=300, type=int, help="Figure DPI.")
    parser.add_argument("--latex", action="store_true", help="Generate LaTeX tables.")
    parser.add_argument("--no-figures", action="store_true", help="Skip figure generation.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose console logging.")
    return parser.parse_args()


def configure_logging(output_dir: Path, verbose: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "log.txt"

    handlers: list[logging.Handler] = [
        logging.FileHandler(log_path, mode="w", encoding="utf-8")
    ]
    if verbose:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
        handlers=handlers,
        force=True,
    )


def infer_from_path(path: Path, input_dir: Path) -> tuple[str, str, str]:
    relative = path.relative_to(input_dir)
    parts = relative.parts
    llm = parts[0] if len(parts) >= 3 else "unknown"
    scenario = parts[1].replace("scenario_", "") if len(parts) >= 3 else "unknown"
    prompt = path.stem
    return llm, prompt, scenario


def canonical_section(title: str) -> str:
    title = title.strip().strip("#").strip()
    title = re.sub(r"\s+", " ", title)
    return title


def parse_markdown(path: Path, input_dir: Path) -> ChecklistResult:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("empty file")

    inferred_llm, inferred_prompt, inferred_scenario = infer_from_path(path, input_dir)
    metadata = {match.group(1).lower(): match.group(2).strip() for match in METADATA_RE.finditer(text)}

    missing = [key for key in ("llm", "prompt", "scenario") if key not in metadata]
    if missing:
        logging.warning("%s: missing metadata %s; inferred from path", path, ", ".join(missing))

    llm = metadata.get("llm", inferred_llm)
    prompt = metadata.get("prompt", inferred_prompt)
    scenario = metadata.get("scenario", inferred_scenario)

    sections: list[str] = []
    criteria: list[Criterion] = []
    notes_lines: list[str] = []
    current_section: str | None = None
    in_notes = False

    for line_number, line in enumerate(text.splitlines(), start=1):
        section_match = SECTION_RE.match(line)
        if section_match:
            title = canonical_section(section_match.group("title"))
            if title.lower() == "notes":
                in_notes = True
                current_section = None
                continue
            in_notes = False
            current_section = title
            sections.append(title)
            continue

        item_match = CHECKLIST_ITEM_RE.match(line)
        if item_match:
            if current_section is None:
                raise ValueError(f"checklist item outside a section at line {line_number}")
            criteria.append(
                Criterion(
                    section=current_section,
                    text=item_match.group("text").strip(),
                    checked=item_match.group("mark").lower() == "x",
                )
            )
            continue

        if in_notes:
            notes_lines.append(line)

    if not sections:
        logging.warning("%s: missing sections", path)
    if not criteria:
        raise ValueError("no checklist criteria found")

    section_counts = Counter(criterion.section for criterion in criteria)
    for section in sections:
        if section_counts[section] == 0:
            logging.warning("%s: empty section '%s'", path, section)

    duplicate_counts = Counter((criterion.section, criterion.text) for criterion in criteria)
    for (section, criterion_text), count in duplicate_counts.items():
        if count > 1:
            logging.warning(
                "%s: duplicate criterion in '%s' (%d times): %s",
                path,
                section,
                count,
                criterion_text,
            )

    return ChecklistResult(
        path=path,
        llm=llm,
        prompt=prompt,
        scenario=scenario,
        sections=tuple(sections),
        criteria=tuple(criteria),
        notes="\n".join(notes_lines).strip(),
    )


def parse_all(input_dir: Path) -> list[ChecklistResult]:
    markdown_files = sorted(input_dir.glob("*/*/*.md"))
    if not markdown_files:
        raise FileNotFoundError(f"No markdown files found under {input_dir}")

    results: list[ChecklistResult] = []
    for path in markdown_files:
        try:
            results.append(parse_markdown(path, input_dir))
        except ValueError as exc:
            logging.error("%s: invalid markdown: %s", path, exc)

    if not results:
        raise ValueError("No valid checklist files were parsed.")
    return results


def percent(value: float) -> float:
    if math.isnan(value):
        return np.nan
    return round(value * 100, 2)


def quality_scores(results: Iterable[ChecklistResult]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for result in results:
        total = len(result.criteria)
        checked = sum(criterion.checked for criterion in result.criteria)
        row: dict[str, object] = {
            "LLM": result.llm,
            "Prompt": result.prompt,
            "Scenario": result.scenario,
            "Total Checked": checked,
            "Total Criteria": total,
            "CQS": percent(checked / total),
        }

        by_section = defaultdict(list)
        for criterion in result.criteria:
            by_section[criterion.section].append(criterion.checked)

        for section in EXPECTED_SECTIONS:
            values = by_section.get(section, [])
            row[section] = percent(sum(values) / len(values)) if values else np.nan

        rows.append(row)

    return pd.DataFrame(rows).sort_values(["LLM", "Scenario", "Prompt"]).reset_index(drop=True)


def criterion_scores(results: Iterable[ChecklistResult]) -> pd.DataFrame:
    aggregate: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"checked": 0, "total": 0})
    for result in results:
        for criterion in result.criteria:
            key = (criterion.text, criterion.section)
            aggregate[key]["checked"] += int(criterion.checked)
            aggregate[key]["total"] += 1

    rows = [
        {
            "Criterion": criterion,
            "Section": section,
            "Checked": counts["checked"],
            "Total": counts["total"],
            "Success Rate": percent(counts["checked"] / counts["total"]),
        }
        for (criterion, section), counts in aggregate.items()
    ]

    return (
        pd.DataFrame(rows)
        .sort_values(["Success Rate", "Section", "Criterion"], ascending=[False, True, True])
        .reset_index(drop=True)
    )


def llm_section_scores(results: Iterable[ChecklistResult]) -> pd.DataFrame:
    aggregate: dict[tuple[str, str], dict[str, object]] = defaultdict(
        lambda: {"checked": 0, "total": 0, "scores": []}
    )
    for result in results:
        checklist_sections: dict[str, list[bool]] = defaultdict(list)
        for criterion in result.criteria:
            key = (result.llm, criterion.section)
            aggregate[key]["checked"] += int(criterion.checked)
            aggregate[key]["total"] += 1
            checklist_sections[criterion.section].append(criterion.checked)

        for section, values in checklist_sections.items():
            key = (result.llm, section)
            aggregate[key]["scores"].append(percent(sum(values) / len(values)))

    rows = []
    section_order = {section: index for index, section in enumerate(EXPECTED_SECTIONS)}
    for (llm, section), counts in aggregate.items():
        scores = pd.Series(counts["scores"], dtype="float64")
        rows.append(
            {
                "LLM": llm,
                "Section": section,
                "Checked": counts["checked"],
                "Total": counts["total"],
                "Mean Score": percent(counts["checked"] / counts["total"]),
                "Std": round(scores.std(ddof=1), 2) if len(scores) > 1 else np.nan,
            }
        )

    return (
        pd.DataFrame(rows)
        .assign(SectionOrder=lambda df: df["Section"].map(section_order).fillna(len(section_order)))
        .sort_values(["LLM", "SectionOrder", "Section"])
        .drop(columns=["SectionOrder"])
        .reset_index(drop=True)
    )


def confidence_interval(values: pd.Series) -> tuple[float, float]:
    if stats is None:
        return (np.nan, np.nan)

    clean = values.dropna().astype(float)
    n = len(clean)
    if n < 2:
        return (np.nan, np.nan)

    mean = clean.mean()
    sem = clean.std(ddof=1) / math.sqrt(n)
    if sem == 0:
        return (round(mean, 2), round(mean, 2))

    low, high = stats.t.interval(0.95, n - 1, loc=mean, scale=sem)
    low = max(0.0, low)
    high = min(100.0, high)
    return (round(low, 2), round(high, 2))


def grouped_summary(df: pd.DataFrame, group_columns: str | list[str], include_ci: bool) -> pd.DataFrame:
    grouped = df.groupby(group_columns, dropna=False)["CQS"]
    summary = grouped.agg(Mean="mean", Std="std", Min="min", Max="max", N="count").reset_index()
    summary[["Mean", "Std", "Min", "Max"]] = summary[["Mean", "Std", "Min", "Max"]].round(2)

    if include_ci:
        intervals = grouped.apply(confidence_interval)
        index_columns = [group_columns] if isinstance(group_columns, str) else group_columns

        def lookup_interval(row: pd.Series) -> tuple[float, float]:
            key = row[index_columns[0]] if len(index_columns) == 1 else tuple(row[column] for column in index_columns)
            return intervals.loc[key]

        summary["CI 95% Low"] = summary.apply(lambda row: lookup_interval(row)[0], axis=1)
        summary["CI 95% High"] = summary.apply(lambda row: lookup_interval(row)[1], axis=1)

    return summary


def section_summary(df: pd.DataFrame) -> pd.DataFrame:
    id_columns = ["LLM", "Prompt", "Scenario"]
    available = [section for section in EXPECTED_SECTIONS if section in df.columns]
    melted = df.melt(id_vars=id_columns, value_vars=available, var_name="Section", value_name="Score")
    return (
        melted.groupby("Section", dropna=False)["Score"]
        .agg(Mean="mean", Std="std", Min="min", Max="max", N="count")
        .round(2)
        .reset_index()
    )


def write_csv_outputs(
    output_dir: Path,
    quality_df: pd.DataFrame,
    criteria_df: pd.DataFrame,
    llm_section_df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    include_ci = stats is not None
    summaries = {
        "llm_summary": grouped_summary(quality_df, "LLM", include_ci),
        "prompt_summary": grouped_summary(quality_df, "Prompt", include_ci),
        "scenario_summary": grouped_summary(quality_df, "Scenario", include_ci),
        "llm_prompt_summary": grouped_summary(quality_df, ["LLM", "Prompt"], include_ci),
        "section_summary": section_summary(quality_df),
    }

    quality_df.to_csv(output_dir / "quality_scores.csv", index=False)
    criteria_df.to_csv(output_dir / "criterion_scores.csv", index=False)
    llm_section_df.to_csv(output_dir / "llm_section_scores.csv", index=False)
    summaries["llm_summary"].to_csv(output_dir / "llm_summary.csv", index=False)
    summaries["prompt_summary"].to_csv(output_dir / "prompt_summary.csv", index=False)
    summaries["scenario_summary"].to_csv(output_dir / "scenario_summary.csv", index=False)
    summaries["llm_prompt_summary"].to_csv(output_dir / "llm_prompt_summary.csv", index=False)
    summaries["section_summary"].to_csv(output_dir / "section_summary.csv", index=False)
    return summaries


def latex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for source, replacement in replacements.items():
        text = text.replace(source, replacement)
    return text


def write_latex_table(df: pd.DataFrame, path: Path, columns: list[str]) -> None:
    selected = df[columns].copy()
    with path.open("w", encoding="utf-8") as handle:
        handle.write("\\begin{tabular}{" + "l" * len(columns) + "}\n")
        handle.write("\\toprule\n")
        handle.write(" & ".join(latex_escape(column) for column in columns) + " \\\\\n")
        handle.write("\\midrule\n")
        for _, row in selected.iterrows():
            handle.write(" & ".join(latex_escape(row[column]) for column in columns) + " \\\\\n")
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")


def write_latex_outputs(output_dir: Path, quality_df: pd.DataFrame, criteria_df: pd.DataFrame) -> None:
    latex_dir = output_dir / "latex"
    latex_dir.mkdir(parents=True, exist_ok=True)

    quality_table = (
        quality_df.groupby(["LLM", "Prompt"], dropna=False)["CQS"]
        .agg(Mean="mean", Std="std")
        .round(2)
        .reset_index()
    )
    write_latex_table(quality_table, latex_dir / "table_quality.tex", ["LLM", "Prompt", "Mean", "Std"])

    sections = [
        column
        for column in EXPECTED_SECTIONS
        if column in quality_df.columns and quality_df[column].notna().any()
    ]
    section_table = (
        quality_df.groupby(["LLM", "Prompt"], dropna=False)[sections]
        .mean()
        .round(2)
        .reset_index()
    )
    write_latex_table(section_table, latex_dir / "table_sections.tex", ["LLM", "Prompt", *sections])

    criteria_table = criteria_df.head(15).copy()
    criteria_table["Criterion"] = criteria_table["Criterion"].map(
        lambda text: textwrap.shorten(str(text), width=70, placeholder="...")
    )
    write_latex_table(
        criteria_table,
        latex_dir / "table_criteria.tex",
        ["Criterion", "Section", "Checked", "Total", "Success Rate"],
    )


def save_bar_chart(df: pd.DataFrame, x: str, y: str, path: Path, title: str, ylabel: str, dpi: int) -> None:
    ordered = df.sort_values(y, ascending=False)
    fig_width = max(6, len(ordered) * 0.8)
    fig, ax = plt.subplots(figsize=(fig_width, 4.5))
    labels = ordered[x].astype(str).tolist()
    positions = np.arange(len(labels))
    ax.bar(positions, ordered[y], color="#4C78A8")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, 100)
    ax.set_xticks(positions, labels=labels, rotation=30, ha="right")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


def save_heatmap(df: pd.DataFrame, path: Path, dpi: int) -> None:
    pivot = df.pivot_table(index="LLM", columns="Prompt", values="CQS", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(max(6, len(pivot.columns) * 1.2), max(4, len(pivot) * 0.8)))
    image = ax.imshow(pivot.fillna(0), cmap="viridis", vmin=0, vmax=100)
    ax.set_xticks(range(len(pivot.columns)), labels=pivot.columns)
    ax.set_yticks(range(len(pivot.index)), labels=pivot.index)
    ax.set_title("Mean CQS by LLM and Prompt")

    for row_index, row_name in enumerate(pivot.index):
        for col_index, col_name in enumerate(pivot.columns):
            value = pivot.loc[row_name, col_name]
            label = "" if pd.isna(value) else f"{value:.1f}"
            ax.text(col_index, row_index, label, ha="center", va="center", color="white")

    fig.colorbar(image, ax=ax, label="CQS (%)")
    fig.tight_layout()
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


def slugify(value: object) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", str(value).strip().lower()).strip("_")
    return slug or "unknown"


def save_radar_chart(llm: str, section_df: pd.DataFrame, path: Path, dpi: int) -> None:
    values_by_section = dict(zip(section_df["Section"], section_df["Mean Score"]))
    labels = EXPECTED_SECTIONS
    values = [float(values_by_section.get(section, 0.0)) for section in labels]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    closed_values = values + values[:1]
    closed_angles = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"polar": True})
    ax.plot(closed_angles, closed_values, color="#4C78A8", linewidth=2)
    ax.fill(closed_angles, closed_values, color="#4C78A8", alpha=0.22)
    ax.set_title(f"{llm} Section Scores", pad=20)
    ax.set_xticks(angles, labels=labels)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"])
    ax.grid(alpha=0.35)
    fig.tight_layout()
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


def save_radar_charts(llm_section_df: pd.DataFrame, figures_dir: Path, dpi: int) -> None:
    for llm, group in llm_section_df.groupby("LLM", sort=True):
        save_radar_chart(str(llm), group, figures_dir / f"radar_{slugify(llm)}.png", dpi)


def write_figures(
    output_dir: Path,
    quality_df: pd.DataFrame,
    summaries: dict[str, pd.DataFrame],
    llm_section_df: pd.DataFrame,
    dpi: int,
) -> None:
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    save_bar_chart(summaries["llm_summary"], "LLM", "Mean", figures_dir / "llm_summary.png", "LLM Performance", "Mean CQS (%)", dpi)
    save_bar_chart(summaries["prompt_summary"], "Prompt", "Mean", figures_dir / "prompt_summary.png", "Prompt Performance", "Mean CQS (%)", dpi)
    save_bar_chart(summaries["scenario_summary"], "Scenario", "Mean", figures_dir / "scenario_summary.png", "Scenario Difficulty", "Mean CQS (%)", dpi)
    save_bar_chart(summaries["section_summary"], "Section", "Mean", figures_dir / "section_summary.png", "Section Scores", "Mean Score (%)", dpi)
    save_heatmap(quality_df, figures_dir / "llm_prompt_heatmap.png", dpi)
    save_radar_charts(llm_section_df, figures_dir, dpi)


def main() -> None:
    args = parse_args()
    output_dir = args.output
    configure_logging(output_dir, args.verbose)

    input_dir = args.input
    results = parse_all(input_dir)
    quality_df = quality_scores(results)
    criteria_df = criterion_scores(results)
    llm_section_df = llm_section_scores(results)
    summaries = write_csv_outputs(output_dir, quality_df, criteria_df, llm_section_df)

    if args.latex:
        write_latex_outputs(output_dir, quality_df, criteria_df)

    if not args.no_figures:
        write_figures(output_dir, quality_df, summaries, llm_section_df, args.dpi)

    logging.info("Parsed %d checklist files.", len(results))
    logging.info("Wrote results to %s.", output_dir)


if __name__ == "__main__":
    main()
