# analyze_checklists.py

`analyze_checklists.py` parses checklist Markdown files under the `analysis/` directory and generates quantitative outputs for model, prompt, scenario, section, and criterion-level analysis.

## Usage

Run the full pipeline with the default directories:

```bash
python3 scripts/analyze_checklists.py
```

Generate LaTeX tables and verbose logs:

```bash
python3 scripts/analyze_checklists.py --latex --verbose
```

## Command-Line Options

- `--input analysis/`: input directory containing checklist Markdown files.
- `--output results/`: output directory for CSV files, logs, figures, and LaTeX tables.
- `--dpi 300`: DPI used when saving figures.
- `--latex`: also generate LaTeX tables under `results/latex/`.
- `--no-figures`: skip figure generation.
- `--verbose`: print progress information to the console.

## Expected Input Layout

The parser expects checklist files in this shape:

```text
analysis/
  <llm>/
    scenario_<id>/
      <prompt>.md
```

Each Markdown file may define metadata using inline backtick fields:

```markdown
`llm: GPT` `prompt: CoT` `scenario: 01`
```

If metadata is missing, the script infers `LLM`, `Prompt`, and `Scenario` from the file path.

## Parsing Rules

- Sections are Markdown headings beginning with `###`.
- Checklist criteria are lines matching `- [x]` or `- [ ]`.
- Checked items count as successful criteria.
- Validation messages are written to `results/log.txt`.
- Empty files and files without checklist criteria are treated as invalid.
- Missing metadata, missing sections, empty sections, and duplicate criteria are logged as warnings.

## Metrics

Scores are expressed as percentages from `0` to `100`.

- `CQS`: checklist quality score, computed as checked criteria divided by total criteria.
- Section score: checked criteria divided by total criteria within a section.
- Criterion success rate: checked appearances divided by total appearances for each unique criterion.
- Summary means and standard deviations are computed from checklist-level CQS values unless noted otherwise.
- Confidence intervals are generated only when `scipy` is available.

## CSV Outputs

### `quality_scores.csv`

One row per checklist file. It contains the checklist metadata, total checked criteria, total criteria, overall `CQS`, and one score column for each expected section:

- `Completeness`
- `Correctness`
- `Clarity`
- `Simplicity`
- `Flexibility`
- `Implementability`

### `criterion_scores.csv`

One row per unique criterion text and section. It reports:

- total checked appearances
- total appearances
- success rate across all parsed checklists

This file is useful for identifying criteria that are consistently satisfied or consistently missed.

### `llm_summary.csv`

Aggregates `CQS` by `LLM`. It reports mean, standard deviation, minimum, maximum, sample size, and confidence interval columns when available.

### `prompt_summary.csv`

Aggregates `CQS` by `Prompt`. It shows how each prompting strategy performs on average across all LLMs and scenarios.

### `scenario_summary.csv`

Aggregates `CQS` by `Scenario`. Lower means indicate harder scenarios under the checklist scoring scheme.

### `llm_prompt_summary.csv`

Aggregates `CQS` by each `LLM` and `Prompt` pair. This file is useful for comparing prompting strategies within each model.

### `section_summary.csv`

Aggregates section scores across all checklists. It reports mean, standard deviation, minimum, maximum, and sample size for each section.

### `llm_section_scores.csv`

Aggregates raw criterion outcomes by `LLM` and `Section`. It reports:

- `Checked`: number of checked criteria for that LLM and section
- `Total`: total criteria evaluated for that LLM and section
- `Mean Score`: `Checked / Total * 100`
- `Std`: standard deviation of checklist-level section scores for that LLM and section

This file is also used to generate the per-LLM radar charts.

## Figure Outputs

When figures are enabled, PNG files are written under `results/figures/`:

- `llm_summary.png`: mean CQS by LLM.
- `prompt_summary.png`: mean CQS by prompt.
- `scenario_summary.png`: mean CQS by scenario.
- `section_summary.png`: mean score by section.
- `llm_prompt_heatmap.png`: mean CQS by LLM and prompt.
- `radar_<llm>.png`: section radar chart for each LLM.

## LaTeX Outputs

When `--latex` is provided, the script writes tables under `results/latex/`:

- `table_quality.tex`: mean and standard deviation by LLM and prompt.
- `table_sections.tex`: average section scores by LLM and prompt.
- `table_criteria.tex`: top criteria by success rate.

