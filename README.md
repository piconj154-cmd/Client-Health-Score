# Client Health Score Calculator

A Python CLI tool that reads BPO client account data, computes a weighted health score for each account, and flags at-risk clients for CSM follow-up.

Built from experience managing multi-industry BPO accounts. The core problem this solves is real: knowing which clients need attention before they churn, and identifying which ones are ready to expand into new products.

---

## What it does

- Reads a CSV of client accounts (exported from Salesforce, HubSpot, or Google Sheets)
- Scores each account across 6 dimensions: **usage**, **engagement**, **support load**, **NPS**, **onboarding status**, and **AI product interest**
- Classifies each account as **Green / Yellow / Red**
- Prints an action summary to the terminal including an **AI upsell pipeline** section
- Exports a full scored report to CSV

---

## Sample output

```
=======================================================
  CLIENT HEALTH SCORE REPORT
  Generated: 2026-03-12
=======================================================
  Total accounts:   25
  Green  (>=75):    14
  Yellow (50-74):   2
  Red    (<50):     9
=======================================================

  ACTION REQUIRED — 9 account(s) below 60.0:

  [Red   ] Nortek Capital            Score:   3.0  Renewal: -308d
  [Red   ] Redstone Power            Score:  19.0  Renewal: -296d
  [Red   ] Solara Financial          Score:  47.8  Renewal: -270d

  AI UPSELL PIPELINE — 10 account(s) to follow up:

  Crestline Bank            Status: in_pilot     Health:  95.0
  Volterra Energy           Status: interested   Health:  93.5
  Solstice Power            Status: in_pilot     Health:  87.2
```

---

## Scoring model

| Dimension      | Weight | What it measures                                        |
|----------------|--------|---------------------------------------------------------|
| Usage          | 25%    | Monthly feature/capacity utilization %                  |
| Engagement     | 25%    | Days since last meaningful CSM contact                  |
| Support load   | 20%    | Open tickets + escalations last 90 days                 |
| NPS            | 15%    | Net Promoter Score (0–10)                               |
| AI Interest    | 10%    | Interest/adoption level of AI products we offer         |
| Onboarding     | 5%     | Whether onboarding is complete                          |

Weights are configurable in `health_score.py` under `WEIGHTS`.

### AI Interest levels

| Value        | Score | Meaning                                  |
|--------------|-------|------------------------------------------|
| `adopted`    | 100   | Already using one of our AI products     |
| `in_pilot`   | 75    | Currently piloting/testing               |
| `interested` | 50    | Had a demo or discovery call             |
| `none`       | 0     | No interest expressed yet                |

---

## Project structure

```
Client-Health-Score/
│
├── health_score.py         # Main script
├── data/
│   └── clients.csv         # Sample input data (25 fictional clients)
├── outputs/
│   └── health_report.csv   # Generated report (git-ignored)
├── test/
│   └── test_health_score.py
├── requirements.txt
└── README.md
```

---

## Getting started

**1. Clone the repo**
```bash
git clone https://github.com/piconj154-cmd/Client-Health-Score.git
cd Client-Health-Score
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

| Column                    | Type          | Example              |
|---------------------------|---------------|----------------------|
| `client_id`               | string        | C001                 |
| `client_name`             | string        | Crestline Bank       |
| `industry`                | string        | Banking              |
| `contract_value`          | number        | 142000               |
| `contract_end_date`       | date          | 2025-10-01           |
| `days_since_last_contact` | int           | 4                    |
| `open_tickets`            | int           | 1                    |
| `monthly_usage_pct`       | int           | 88                   |
| `nps_score`               | int           | 9                    |
| `onboarding_complete`     | yes/no        | yes                  |
| `escalations_last_90d`    | int           | 0                    |
| `ai_interest`             | none/interested/in_pilot/adopted | in_pilot |

---

## Running tests

```bash
python -m pytest test/ -v
```

23 tests covering all individual scorers, risk label thresholds, and end-to-end healthy/at-risk client scenarios.

---

## Next steps / roadmap

- [ ] Swap CSV storage for SQLite
- [ ] Add trend tracking — score changes over time
- [ ] Build a Streamlit dashboard on top of this
- [ ] Connect to Salesforce API instead of manual CSV export

---

## About

Built by Jose Guillermo Picon as part of a Python learning path, with a focus on Customer Success Management in BPO environments.

Python concepts used: `csv`, `argparse`, `datetime`, functions, conditionals, dictionaries, file I/O.
