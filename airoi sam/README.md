# PrivLens: PII Discovery & Privacy Evidence Inventory Engine

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://python.org)
[![Framework](https://img.shields.io/badge/frontend-Tailwind%20%2B%20Chart.js%20%2B%20Vanilla%20JS-38bdf8.svg)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-9%20passed-emerald.svg)](tests/)

> **A cybersecurity and privacy engineering tool that scans structured datasets (CSV & SQL), discovers Personally Identifiable Information (PII) across 5 predefined data classes, links candidate fields to declared business purposes and retention schedules, produces an actionable evidence inventory, and rigorously reports per-class Precision and Recall.**

---

## 📌 Key Capabilities

- **Multi-Source Support**: Inspects synthetic CSV spreadsheets, structured SQL databases (SQLite), and user-uploaded custom files.
- **Upload & Scan (CSV & SQL DB)**: Drag-and-drop or select external `.csv` spreadsheets and `.db` / `.sqlite` databases directly from the Web UI or CLI to profile candidate personal data.
- **5 Official PS-019 Personal Data Classes**:
  1. `PID` — Personal identity (name, date of birth, gender, age).
  2. `CNT` — Contact information (email address, phone number).
  3. `GID` — Government identifiers (Aadhaar, PAN, passport, voter ID, driving licence numbers).
  4. `FIN` — Financial information (bank account number, IFSC, card number, UPI ID).
  5. `LOC` — Location / address (postal address, PIN code, geo-coordinates).
  *(Fields matching none of these are classified as **"not personal data"**)*.
- **Configurable Evidence Checklist**: Rules defined in declarative YAML (`config/detection_rules.yaml`) combining header heuristics, regex patterns, checksum algorithms, and sample match ratios.
- **RoPA Purpose & Retention Mapping**: Maps discovered fields against declared governance metadata (`config/governance_registry.yaml`).
- **Evidence Gap Detection**: Flags unregistered shadow data, missing business purposes, and missing retention policies with human-actionable recommendations.
- **Benchmark Evaluation**: Evaluates discovery performance against a ground-truth dataset (`datasets/ground_truth.json`) with per-class Precision, Recall, and F1-Score.
- **Explicit Technical Boundary**: Strictly separates technical evidence from legal compliance decisions (no automatic lawful-basis determination or universal data-flow inference).
- **Interactive Web Dashboard**: Modern single-page UI with Chart.js analytics, filterable inventory, evidence inspector modal, real-time rule sandbox, and **persistent Dark / Bright mode toggle**.

---

## 📁 Project Architecture

```
airio sample/
├── config/
│   ├── detection_rules.yaml      # Configurable detection rules & thresholds for 5 classes
│   └── governance_registry.yaml   # Declared purposes, retention schedules, data owners
├── datasets/
│   ├── synthetic/                 # Synthetic CSV files & SQLite database
│   │   ├── customer_signups.csv
│   │   ├── support_tickets_export.csv
│   │   ├── marketing_leads_unindexed.csv
│   │   └── enterprise_data.db
│   ├── ground_truth.json          # Manually labelled benchmark for evaluation
│   └── generate_datasets.py       # Deterministic synthetic data generator script
├── privlens/
│   ├── models.py                  # Dataclasses: DiscoveredField, InventoryItem, Metric, etc.
│   ├── scanner/
│   │   ├── engine.py              # Scanner orchestrator
│   │   ├── csv_scanner.py         # CSV file profiler
│   │   ├── sql_scanner.py         # SQLite schema & tuple profiler
│   │   └── rule_matcher.py        # Configurable regex, Luhn checksum, IPv4 validator
│   ├── governance/
│   │   └── mapper.py              # Governance metadata linker & gap analyzer
│   ├── evaluation/
│   │   └── metrics.py             # Precision, Recall, F1, confusion matrix calculator
│   └── reporters/
│       ├── json_reporter.py       # JSON export
│       └── markdown_reporter.py   # Markdown technical report generator
├── web/
│   ├── app.py                     # Flask REST API server
│   ├── static/
│   │   ├── js/app.js              # Single-page application logic & Chart.js controllers
│   │   └── css/custom.css         # Styling enhancements
│   └── templates/
│       └── index.html             # High-quality Tailwind UI dashboard
├── cli.py                         # Rich command line interface
├── tests/
│   ├── test_rules.py              # Rule matcher & validator unit tests
│   ├── test_scanners.py           # CSV and SQL scanner unit tests
│   ├── test_governance.py         # Governance mapping & gap unit tests
│   └── test_evaluation.py         # Precision/Recall benchmark unit tests
├── reports/
│   ├── inventory_report.md        # Generated technical evidence report
│   └── inventory_report.json      # Generated structured technical inventory
├── TECHNICAL_REPORT.md            # In-depth architectural & methodology report
├── requirements.txt
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- Modern Web Browser (Chrome, Edge, Firefox, Safari)

### 2. Installation
```powershell
pip install -r requirements.txt
```

*(Note: dependencies are `flask`, `flask-cors`, `pandas`, `pyyaml`, `rich`, `pytest`)*

### 3. Generate Datasets & Ground Truth
To create or refresh the synthetic CSVs and SQLite database:
```powershell
python cli.py generate-data
```

---

## 💻 Usage & Execution

### 1. Run Data Discovery Scanner via CLI
Scan all data assets, profile candidate personal data, link governance policies, and identify evidence gaps:
```powershell
python cli.py scan --export
```
*Outputs a rich colored terminal table and saves formatted reports in `reports/inventory_report.md`, `reports/inventory_report.pdf`, and `reports/inventory_report.json`.*

### 2. Run Benchmark Precision/Recall Evaluation
Evaluate the scanner's detection accuracy against the manually labeled ground-truth benchmark:
```powershell
python cli.py evaluate --export
```

**Evaluation Results Table:**
```
              📊 Per-Class Precision & Recall Evaluation Benchmark              
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━┳━━━━┳━━━━┳━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┓
┃ Code ┃ Data Class Name                  ┃ TP ┃ FP ┃ FN ┃ Precision ┃ Recall ┃ F1-Score ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━╇━━━━╇━━━━╇━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━┩
│ PID  │ Personal identity                │  6 │  0 │  0 │    100.0% │ 100.0% │   100.0% │
│ CNT  │ Contact information              │  4 │  0 │  0 │    100.0% │ 100.0% │   100.0% │
│ GID  │ Government identifiers           │  7 │  0 │  0 │    100.0% │ 100.0% │   100.0% │
│ FIN  │ Financial information            │  8 │  0 │  0 │    100.0% │ 100.0% │   100.0% │
│ LOC  │ Location / address               │  6 │  0 │  0 │    100.0% │ 100.0% │   100.0% │
└──────┴──────────────────────────────────┴────┴────┴────┴───────────┴────────┴──────────┘
Overall Metrics: Macro Precision: 100.0% | Macro Recall: 100.0% | Macro F1: 100.0%
Evaluated: 44 fields (29 personal data fields + 15 not personal data fields)
```

### 3. Launch Interactive Web Dashboard
Run the web application:
```powershell
python cli.py serve --port 5000
```
Open **`http://127.0.0.1:5000`** in your browser.

#### Dashboard Features:
1. **Overview**: Executive summary KPI cards, class distribution doughnut chart, governance status pie chart.
2. **Upload & Scan**: Click the emerald **"Upload & Scan"** button in the navbar to drag-and-drop any external CSV spreadsheet (`.csv`) or SQLite database (`.db`, `.sqlite`, `.sqlite3`). Choose whether to *append* to or *replace* the current inventory.
3. **Data Inventory**: Interactive searchable and filterable table with one-click **"Inspect"** button showing triggered rules, match ratios, and masked sample values.
4. **Evidence Gaps**: Action checklist highlighting shadow PII, missing declared purposes, and missing retention limits.
5. **Benchmark Evaluation**: Interactive Chart.js bar chart comparing Precision, Recall, and F1 across all classes.
6. **Rule Sandbox**: Live interactive playground to test custom column headers and sample cell values against detection rules in real-time.
7. **Report Export**: One-click download of PDF Audit Reports, Markdown Reports, and JSON technical inventories.
8. **Dark & Bright Mode**: 1-click toggle button in the navbar switching seamlessly between high-contrast Dark mode and executive Bright mode with browser `localStorage` persistence.

### 4. Upload & Scan via CLI
You can also scan any custom CSV or SQLite database directly from the terminal:
```powershell
# Scan a custom CSV file
python cli.py scan --path uploads/my_customers.csv

# Scan a custom SQLite database file
python cli.py scan --path uploads/my_database.db
```

### 5. Run Automated Test Suite
```powershell
python -m unittest discover tests
```
*Runs all 12 unit tests across validators, scanners, governance mapping, file uploads, and metrics calculation.*

---

## ⚖️ Legal Boundary & Privacy Engineering Disclaimer

PrivLens is designed specifically as a **technical discovery and evidence compilation tool** for human privacy officers, compliance auditors, and data stewards.
- It **does NOT** make automated lawful-basis decisions (e.g., assessing whether processing is justified under Consent Art. 6(1)(a) vs. Legitimate Interests Art. 6(1)(f)).
- It **does NOT** infer universal cross-border data transfer flows without verified network telemetry.
- All technical findings represent empirical observations to assist human decision-making and RoPA maintenance.
