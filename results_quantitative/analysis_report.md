# Quantitative analysis report

The analysis covers 18 outputs (2 models x 3 prompting techniques x 3 scenarios). 
CQS is the percentage of the 26 checklist items marked as satisfied. Dimension scores are calculated within each checklist dimension.

## Main CQS table

| Model | Prompt | Completeness | Correctness | Clarity | Simplicity | Flexibility | Implementability | CQS Mean | CQS SD | Macro CQS | Rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.1 | CoT + Verifier | 33.33 | 50.00 | 93.33 | 86.67 | 77.78 | 50.00 | 65.38 | 11.54 | 65.19 | 1.00 |
| GPT-5.1 | CoT | 26.67 | 38.89 | 86.67 | 86.67 | 66.67 | 50.00 | 58.97 | 16.01 | 59.26 | 2.00 |
| Qwen-3 | CoT + Verifier | 0.00 | 44.44 | 100.00 | 86.67 | 33.33 | 33.33 | 52.56 | 4.44 | 49.63 | 3.00 |
| Qwen-3 | CoT | 0.00 | 44.44 | 86.67 | 80.00 | 44.44 | 33.33 | 50.00 | 6.66 | 48.15 | 4.00 |
| GPT-5.1 | One-shot | 33.33 | 22.22 | 73.33 | 73.33 | 33.33 | 50.00 | 47.44 | 9.68 | 47.59 | 5.00 |
| Qwen-3 | One-shot | 6.67 | 33.33 | 60.00 | 86.67 | 55.56 | 50.00 | 47.44 | 5.88 | 48.70 | 5.00 |

## Gold-standard comparison

| Model | Prompt | Entity F1 | Attribute F1 | Relation F1 | Cardinality Accuracy | Structural F1 | ROUGE-L | BLEU-4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.1 | CoT + Verifier | 83.96 | 40.68 | 65.03 | 90.60 | 63.22 | 44.68 | 9.44 |
| GPT-5.1 | CoT | 84.51 | 41.20 | 66.75 | 90.60 | 64.15 | 45.32 | 10.23 |
| GPT-5.1 | One-shot | 74.03 | 39.23 | 62.78 | 95.99 | 58.68 | 42.60 | 9.75 |
| Qwen-3 | CoT + Verifier | 64.55 | 35.39 | 37.58 | 90.00 | 45.84 | 37.47 | 4.12 |
| Qwen-3 | CoT | 64.55 | 35.49 | 36.34 | 75.71 | 45.46 | 37.35 | 4.04 |
| Qwen-3 | One-shot | 69.63 | 33.29 | 39.42 | 93.33 | 47.45 | 38.10 | 4.33 |

## Blocked factorial permutation tests

| Effect | df | F | Permutation p | Partial eta squared |
| --- | --- | --- | --- | --- |
| Model | 1.00 | 2.19 | 0.16 | 0.18 |
| Prompt | 2.00 | 1.87 | 0.19 | 0.27 |
| Model x Prompt | 2.00 | 0.60 | 0.57 | 0.11 |

## Planned descriptive contrasts

| Contrast | Mean difference | SD difference | Standardized paired effect (dz) |
| --- | --- | --- | --- |
| GPT-5.1 - Qwen-3 | 7.26 | 14.45 | 0.50 |
| CoT - One-shot | 7.05 | 17.78 | 0.40 |
| CoT + Verifier - CoT | 4.49 | 7.46 | 0.60 |

## Interpretation

The highest mean CQS was obtained by GPT-5.1 with CoT + Verifier (65.38%, SD=11.54).
Because each model-prompt combination has only three scenario-level observations, inferential results are exploratory. Effect sizes and scenario-level consistency should be considered together with permutation p-values.
ROUGE-L and BLEU-4 were computed over canonicalized schema-feature sequences and are secondary lexical-overlap measures; structural precision, recall and F1 are more appropriate for semantically equivalent ER designs.
