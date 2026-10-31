# ⚡ EV Intelligence
### End-to-End Electric Vehicle Charging Analytics Platform

An end-to-end Data Engineering and Analytics portfolio project that turns raw EV charging records into a clean analytical database and an interactive operations dashboard.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Pandas](https://img.shields.io/badge/Data-Pandas-150458)
![Database](https://img.shields.io/badge/Database-SQLite-003B57)
![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B)
![Tests](https://img.shields.io/badge/Tests-pytest-green)

## 1. Project overview

EV charging networks generate operational data every time a vehicle connects to a charger. Network operators need to understand where charging demand is growing, which stations are busiest, how much energy is delivered, what revenue is generated, and how reliably charging sessions complete.

**EV Intelligence** is a small but complete analytics platform that addresses those questions.

It includes:
- Three realistic source datasets: charging sessions, charging stations, and EV vehicles.
- An ETL pipeline with extraction, validation, transformation, and loading stages.
- A relational SQLite analytics database organized as a simple star schema.
- SQL-based metrics and reusable analytical queries.
- An interactive Streamlit dashboard.
- Automated tests for core pipeline behavior.
- A Dockerfile for containerized execution.

The repository ships with deterministic sample data. No API key, paid service, or cloud account is required.

## 2. Architecture

```text
         RAW CSV DATA
   ┌──────────┬───────────┐
   │ Sessions │ Stations  │ Vehicles
   └─────┬────┴─────┬─────┘
         └─────┬────┘
               ▼
       EXTRACT (Pandas)
               ▼
       VALIDATE DATA
  schema • keys • values • references
               ▼
      TRANSFORM / CLEAN
 timestamps • calendar fields • rounding
               ▼
        LOAD (SQLite)
       ┌───────┴────────┐
       ▼                ▼
  DIMENSIONS         FACT TABLE
 stations, vehicles  charging sessions
       └───────┬────────┘
               ▼
        SQL ANALYTICS
               ▼
      STREAMLIT DASHBOARD
```

## 3. Repository structure

```text
EV-Intelligence/
├── app.py
├── README.md
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── Makefile
├── LICENSE
├── data/
│   └── raw/
│       ├── charging_sessions.csv
│       ├── stations.csv
│       └── vehicles.csv
├── src/
│   └── evintel/
│       ├── __init__.py
│       ├── config.py
│       ├── pipeline.py
│       ├── analytics.py
│       └── cli.py
├── sql/
│   └── analytics_examples.sql
├── tests/
│   └── test_pipeline.py
└── reports/
```

## 4. Technology stack

| Technology | Role |
|---|---|
| Python | Pipeline orchestration and application logic |
| Pandas | CSV ingestion and data transformation |
| SQLite | Local analytical data warehouse |
| SQL | Aggregations, joins, trends, rankings |
| Streamlit | Interactive analytics dashboard |
| pytest | Automated pipeline tests |
| Docker | Reproducible container deployment |

## 5. Dataset

The included synthetic dataset contains:
- **1,800** charging session records.
- **30** charging stations across six Indian cities.
- **80** electric vehicles across multiple vehicle models.
- Four charging network operators.
- Multiple connector types, charger power ratings, payment methods, and session outcomes.

### Data model

**`dim_stations`** — station attributes, city, operator, connector, charger power, and location.

**`dim_vehicles`** — vehicle model, battery capacity, and segment.

**`fact_charging_sessions`** — session identifier, station and vehicle keys, timestamp, duration, energy, amount, status, and payment method.

The fact table references both dimensions through foreign keys. The model is intentionally compact and suitable for learning dimensional modeling.

## 6. Quick start

### Prerequisites

- Python 3.10 or newer
- pip
- Git (for publishing to GitHub)

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/EV-Intelligence.git
cd EV-Intelligence
```

### Step 2 — Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4 — Run the ETL pipeline

```bash
python -m src.evintel.pipeline
```

Expected output resembles:

```text
INFO | Extracting raw CSV files
INFO | Loaded 1800 sessions into .../data/ev_intelligence.db
{'sessions_loaded': 1800, 'stations_loaded': 30, 'vehicles_loaded': 80, ...}
```

The pipeline creates `data/ev_intelligence.db` locally.

### Step 5 — Launch the dashboard

```bash
streamlit run app.py
```

Streamlit prints a local URL, normally `http://localhost:8501`. Open it in your browser.

### Step 6 — Run tests

```bash
pytest -q
```

## 7. Dashboard capabilities

The dashboard presents:
- Total charging sessions and completed sessions.
- Total energy delivered in kWh.
- Revenue in Indian rupees.
- Session completion rate.
- Monthly charging demand.
- Energy delivered by city.
- Hourly charging demand.
- Operator reliability.
- Top charging stations.
- City-level performance details.

Use the sidebar's **Refresh data pipeline** control to rebuild the local database from the bundled CSVs.

## 8. Analytical questions answered

1. Which city accounts for the highest energy consumption?
2. Which stations handle the most charging sessions?
3. Which operator has the highest session completion rate?
4. At what hours is charging demand highest?
5. How does monthly energy demand change?
6. Which vehicle charging sessions contribute to network revenue?

Open `sql/analytics_examples.sql` for standalone SQL queries, including a window-function ranking example.

## 9. Data quality and engineering decisions

The pipeline checks:
- Required columns exist.
- Primary identifiers are unique and non-null.
- Energy, duration, and amount values are valid.
- Session statuses belong to the accepted set.
- Session station and vehicle references exist in the dimension datasets.
- Timestamps can be parsed.

Timestamps are normalized to UTC. Calendar date, hour, and month fields are derived during transformation. The source CSVs are retained unchanged so the pipeline can be rerun.

## 10. Run with Docker

Build:

```bash
docker build -t ev-intelligence .
```

Run:

```bash
docker run --rm -p 8501:8501 ev-intelligence
```

Then open `http://localhost:8501`.

## 11. Future enhancements

- Ingest live station availability from a public charging network API.
- Add Apache Airflow scheduling and retry handling.
- Store raw and curated datasets in Amazon S3 Bronze/Silver/Gold layers.
- Migrate the warehouse from SQLite to PostgreSQL or Snowflake.
- Add dbt models, tests, and documentation.
- Add geospatial station maps and demand heatmaps.
- Forecast station-level demand using time-series models.
- Add anomaly detection for unusual energy, duration, or failure patterns.
- Add role-based access and deployment to a cloud platform.

## 12. Limitations

This is a portfolio and learning project. The sample records are synthetic and do not represent actual charging transactions or live station availability. Revenue is simulated using generated session amounts. The dashboard is descriptive analytics, not a live network control system.

## 13. Author

**Your Name**  
Computer Science & Engineering — AI & ML  
Interests: Data Engineering | SQL | Python | EV Analytics

---

If you find this project useful, consider starring the repository ⭐
