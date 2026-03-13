# Client Health Score Calculator

A Python CLI tool that reads BPO client account data, computes a weighted health score for each account, and flags at-risk clients for CSM follow-up.

Built as part of a CS → Data path, this project reflects a real problem in Customer Success: knowing which accounts need attention before they churn.

---

## What it does

- Reads a CSV of client accounts (exported from Salesforce, HubSpot, or Google Sheets)
- Scores each account across 5 dimensions: **usage**, **engagement**, **support load**, **NPS**, and **onboarding status**
- Classifies each account as **Green / Yellow / Red**
- Prints an action summary to the terminal
- Exports a full scored report to CSV

---

## Sample output

```
=======================================================
  CLIENT HEALTH SCORE REPORT
  Generated: 2025-03-12
=======================================================
  Total accounts:   10
  Green  (>=75):    4
  Yellow (50-74):   3
  Red    (<50):     3
=======================================================

  ACTION REQUIRED — 5 account(s) below 60:

  [Red   ] Atlas Customer Co        Score:  10.5  Renewal: 12d
  [Red   ] Clearpath Services       Score:  18.8  Renewal: 58d
  [Red   ] Orion Outsourcing        Score:  24.5  Renewal: 22d
```

---

## Scoring model

| Dimension      | Weight | What it measures                         |
|----------------|--------|------------------------------------------|
| Usage          | 30%    | Monthly feature/capacity utilization %   |
| Engagement     | 25%    | Days since last meaningful CSM contact   |
| Support load   | 20%    | Open tickets + escalations last 90 days  |
| NPS            | 15%    | Net Promoter Score (0–10)                |
| Onboarding     | 10%    | Whether onboarding is complete           |

Weights are configurable in `health_score.py` under `WEIGHTS`.

---

## Project structure

```
client-health-score/
│
├── health_score.py         # Main script
├── data/
│   └── clients.csv         # Sample input data
├── outputs/
│   └── health_report.csv   # Generated report (git-ignored)
├── tests/
│   └── test_health_score.py
├── requirements.txt
└── README.md
```

---

## Getting started

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/client-health-score.git
cd client-health-score
```

**2. Install dependencies** (none beyond standard library — no pip install needed)

**3. Run with sample data**
```bash
python health_score.py
```

**4. Use your own data**
```bash
python health_score.py --input path/to/your_export.csv --output outputs/my_report.csv
```

**5. Adjust the at-risk threshold**
```bash
python health_score.py --threshold 70
```

---

## Input CSV format

Your CSV needs these columns (export from Salesforce or Google Sheets):

| Column                  | Type    | Example        |
|-------------------------|---------|----------------|
| `client_id`             | string  | C001           |
| `client_name`           | string  | Nexora Solutions |
| `industry`              | string  | Insurance      |
| `contract_value`        | number  | 85000          |
| `contract_end_date`     | date    | 2025-09-15     |
| `days_since_last_contact` | int   | 5              |
| `open_tickets`          | int     | 1              |
| `monthly_usage_pct`     | int     | 87             |
| `nps_score`             | int     | 8              |
| `onboarding_complete`   | yes/no  | yes            |
| `escalations_last_90d`  | int     | 0              |

---

## Running tests

```bash
python -m pytest tests/ -v
```

---

## Next steps / roadmap

- [ ] Swap CSV storage for SQLite (next step: SQL for Data Science)
- [ ] Add trend tracking — score changes over time
- [ ] Build a Streamlit dashboard on top of this (later in learning path)
- [ ] Connect to Salesforce API instead of manual CSV export

---

## About

Built by [Your Name] as part of a Python → Data Science learning path, with a focus on Customer Success Management in BPO environments.

Python concepts used: `csv`, `argparse`, `datetime`, functions, conditionals, dictionaries, file I/O.
