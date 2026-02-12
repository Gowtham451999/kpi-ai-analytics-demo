# KPI AI Analytics Demo (Product Analytics + Narratives)

A small analytics engineering project that:
- Generates synthetic product event data (signup/active events + A/B variants)
- Builds analytics-ready metrics (retention + variant comparison)
- Produces KPI outputs in a repeatable pipeline format

## Why this project
This repo demonstrates analytics engineering fundamentals:
- data generation (test data)
- pipeline-style transformations (clean → metric computation)
- reproducible runs (scripts + requirements)
- documentation-first workflow

## Project structure
kpi-ai-analytics-demo/
src/
generate_data.py
analyze.py
data/
events.csv
requirements.txt
.gitignore

**outputs**
outputs/summary.txt

outputs/ab_d1_retention.csv (A/B table)

outputs/retention_curve.csv (D0–D7 retention)

outputs/retention_curve.png (chart)
