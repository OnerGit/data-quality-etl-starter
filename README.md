# Data Quality ETL Starter

Small teams often receive messy CSV, Excel, JSON, or API data before reporting. This project shows how to turn those inputs into a repeatable Python workflow that validates, cleans, exports, and documents the data quality of each run.

It is designed as a practical GitHub portfolio project for lightweight data cleaning, validation, reporting automation, and ETL work. The goal is not to build an enterprise data platform, but to demonstrate a small workflow that can be understood, run, tested, and adapted.

## What problem this solves

Many small-team data problems are not big data problems. They are repeatability, validation, and handoff problems.

Typical issues include:

- messy CSV or Excel exports from different tools;
- inconsistent column names;
- missing values and duplicate rows;
- invalid email, date, or number formats;
- nested JSON that must become reporting-ready tables;
- API-style JSON responses that need to be flattened and exported;
- manual Excel cleanup repeated every week;
- no data quality report for handoff;
- larger generated test data needed before a workflow can be trusted;
- cleaned files that need to become analytics-ready CSV / Parquet outputs.

## What this project does

This starter workflow can:

- read CSV, Excel, JSON, and mock API data;
- flatten nested JSON into a table;
- normalize column names into stable `snake_case` names;
- validate expected columns and schema rules with Pydantic models;
- detect missing values, duplicate rows, bad email formats, bad dates, and bad numbers;
- clean text values and drop duplicate rows;
- export cleaned CSV output;
- export cleaned data to SQLite by default;
- optionally export to PostgreSQL;
- generate Markdown and JSON data quality reports;
- optionally expose the validation workflow through a FastAPI service layer;
- optionally generate larger synthetic order data for validation demos;
- optionally export analytics-ready CSV and Parquet files;
- optionally query Parquet output locally with DuckDB;
- run through a CLI, pytest tests, and Docker.

## Example workflow

```text
messy CSV / Excel / JSON / mock API
        ↓
read and flatten
        ↓
normalize columns
        ↓
validate expected schema rules
        ↓
clean duplicate rows and text values
        ↓
export cleaned CSV + SQLite / optional PostgreSQL
        ↓
generate data quality report
```

v0.3.0 adds an optional API validation path:

```text
CSV / Excel / JSON file upload
        ↓
FastAPI /validate endpoint
        ↓
reuse the shared workflow service
        ↓
return quality report JSON
        ↓
optional local report file output
```

v0.4.0 adds an optional analytics-ready path:

```text
generated messy order data
        ↓
existing validation and cleaning logic
        ↓
cleaned CSV
        ↓
cleaned Parquet
        ↓
DuckDB query demo
        ↓
summary CSV tables + benchmark report
```

## Tech stack

- Python
- pandas
- Pydantic
- SQLite
- SQLAlchemy-ready optional PostgreSQL export
- FastAPI optional validation service
- Parquet optional analytics-ready export
- DuckDB optional local analytics query demo
- pytest
- Docker

## Project structure

```text
data-quality-etl-starter/
├── data/
│   ├── input/
│   ├── expected/
│   └── output/
├── docs/
├── screenshots/
├── scripts/
│   ├── generate_sample_data.py
│   └── run_analytics_demo.py
├── src/dq_etl_starter/
│   ├── api.py
│   ├── cli.py
│   ├── services.py
│   ├── analytics.py
│   └── ...
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Quick start

```bash
git clone https://github.com/OnerGit/data-quality-etl-starter.git
cd data-quality-etl-starter
python -m venv .venv
```

Activate the virtual environment:

```bash
# macOS / Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.venv\Scripts\activate
```

Install dependencies and the local package:

```bash
pip install -r requirements.txt
pip install -e .
```

The editable install step is recommended because the source code uses a `src/` layout.

## Run with sample CSV

```bash
python -m dq_etl_starter.cli run \
  --input data/input/messy_customers.csv \
  --input-type csv \
  --schema data/expected/customer_schema.json \
  --output-dir data/output/csv \
  --db-target sqlite \
  --table-name cleaned_customers
```

Expected outputs:

```text
data/output/csv/cleaned_customers.csv
data/output/csv/etl_output.sqlite
data/output/csv/quality_report.md
data/output/csv/quality_report.json
```

## Run with sample Excel

```bash
python -m dq_etl_starter.cli run \
  --input data/input/messy_orders.xlsx \
  --input-type excel \
  --schema data/expected/order_schema.json \
  --output-dir data/output/excel \
  --db-target sqlite \
  --table-name cleaned_orders
```

## Run with nested JSON

```bash
python -m dq_etl_starter.cli run \
  --input data/input/nested_orders.json \
  --input-type json \
  --records-path data.orders \
  --schema data/expected/order_schema.json \
  --output-dir data/output/json \
  --db-target sqlite \
  --table-name cleaned_orders
```

## Run with mock API JSON

```bash
python -m dq_etl_starter.cli run \
  --input data/input/mock_api_orders.json \
  --input-type mock-api \
  --schema data/expected/order_schema.json \
  --output-dir data/output/mock_api \
  --db-target sqlite \
  --table-name cleaned_orders
```

## Optional PostgreSQL export

SQLite remains the default local workflow. PostgreSQL is optional and is useful when the delivery target is a real database table.

Start local PostgreSQL:

```bash
docker compose up -d postgres
```

Set `DATABASE_URL` and run the CLI:

```bash
DATABASE_URL=postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo \
python -m dq_etl_starter.cli run \
  --input data/input/messy_customers.csv \
  --input-type csv \
  --schema data/expected/customer_schema.json \
  --output-dir data/output/postgres \
  --db-target postgres \
  --table-name cleaned_customers
```

Windows PowerShell:

```powershell
$env:DATABASE_URL="postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo"

python -m dq_etl_starter.cli run `
  --input data/input/messy_customers.csv `
  --input-type csv `
  --schema data/expected/customer_schema.json `
  --output-dir data/output/postgres `
  --db-target postgres `
  --table-name cleaned_customers
```

See [`docs/postgres.md`](docs/postgres.md) for full PostgreSQL instructions.

## Optional FastAPI validation service

Start the API service:

```bash
uvicorn dq_etl_starter.api:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Useful endpoints:

- `GET /health`
- `POST /validate`

The API is a thin wrapper around the shared workflow service. The CLI workflow remains the source of truth.

See [`docs/api.md`](docs/api.md) for full API instructions.

## Optional analytics-ready export

v0.4.0 adds a larger generated data and analytics-ready export demo. It can generate synthetic customer/order-style data, run the existing validation and cleaning logic, export cleaned CSV and Parquet files, query the Parquet output with DuckDB, and produce lightweight summary tables and a benchmark report.

This path is useful for showing that the workflow is not limited to tiny demo files. It is still intentionally local, small, and reproducible.

Generate 1,000 rows:

```bash
python scripts/generate_sample_data.py \
  --rows 1000 \
  --output data/generated/orders_1k.csv \
  --seed 42
```

Generate 100,000 rows:

```bash
python scripts/generate_sample_data.py \
  --rows 100000 \
  --output data/generated/orders_100k.csv \
  --seed 42
```

Run the analytics demo:

```bash
python scripts/run_analytics_demo.py \
  --input data/generated/orders_100k.csv \
  --schema data/expected/generated_order_schema.json \
  --output-dir data/output/analytics
```

Expected outputs:

```text
data/output/analytics/cleaned_orders.csv
data/output/analytics/cleaned_orders.parquet
data/output/analytics/customer_summary.csv
data/output/analytics/revenue_by_country.csv
data/output/analytics/orders_by_month.csv
data/output/analytics/source_system_summary.csv
data/output/analytics/analytics_queries.sql
data/output/analytics/benchmark_report.md
```

Example DuckDB query:

```sql
SELECT country, ROUND(SUM(revenue), 2) AS total_revenue, COUNT(*) AS order_count
FROM read_parquet('data/output/analytics/cleaned_orders.parquet')
GROUP BY country
ORDER BY total_revenue DESC
LIMIT 10;
```

See [`docs/analytics.md`](docs/analytics.md) for full analytics-ready export instructions.

## Screenshots

The screenshots are designed to support GitHub README, Dev.to articles, Upwork portfolio entries, and proposal references.

Recommended v0.4 screenshots:

- `screenshots/11_generated_data_100k.png`
- `screenshots/12_analytics_outputs.png`
- `screenshots/13_duckdb_query.png`
- `screenshots/14_benchmark_report.png`

See [`screenshots/README.md`](screenshots/README.md) for capture notes.

## Tests

Run all tests:

```bash
python -m compileall -q src/dq_etl_starter
pytest
```

Run v0.4 analytics tests:

```bash
pytest tests/test_generate_sample_data.py
pytest tests/test_analytics.py
pytest tests/test_exporters_parquet.py
```

PostgreSQL integration tests should remain optional and should be skipped unless `DATABASE_URL` is available.

## Docker

Build and run the default workflow:

```bash
docker build -t data-quality-etl-starter:0.4.0 -t data-quality-etl-starter:latest .
docker run --rm data-quality-etl-starter:0.4.0
```

Docker should not change the default project identity. The default run remains a simple reproducible CLI workflow.

## Version roadmap

| Version | Main goal | Business value | Technical scope |
|---|---|---|---|
| v0.1.0 | Local CLI workflow baseline | Proves repeatable data cleaning and validation workflow | pandas, Pydantic, SQLite, Markdown report, pytest, Docker |
| v0.2.0 | PostgreSQL optional export | Adds database delivery capability for client projects | SQLAlchemy engine, PostgreSQL export, Docker Compose, integration docs |
| v0.3.0 | FastAPI validation service | Turns CLI workflow into an API demo with Swagger UI | FastAPI, Pydantic request/response models, upload/validate endpoint |
| v0.4.0 | Larger generated data + analytics-ready export | Proves workflow can handle more realistic data volume | generated data, benchmark report, Parquet, DuckDB |
| v0.5.0 | BI-ready optional demo | Shows cleaned data can support dashboards/reporting | PostgreSQL + optional Metabase demo, summary tables |
| v0.6.0 | AI-ready data preparation | Prepares clean, documented, machine-readable data for later ML/AI workflows | data dictionary, schema profile, feature-ready output |

## What this project is not

This project is intentionally not:

- a production data warehouse;
- an Airflow/dbt/Snowflake/Databricks/PySpark project;
- a full backend application;
- a complex BI platform;
- a user management system;
- an LLM data cleaning tool;
- a RAG chatbot;
- an AI agent.

The design goal is small, runnable, testable, screenshot-ready, and directly useful as Upwork proposal evidence.

## Upwork proposal mapping

This repository can support proposals for:

- CSV cleanup;
- Excel cleanup;
- JSON to CSV;
- API to CSV;
- data validation;
- data quality reporting;
- reporting automation;
- lightweight ETL;
- SQLite export;
- PostgreSQL export;
- FastAPI data validation service;
- analytics-ready CSV / Parquet preparation;
- DuckDB local analytics demo;
- summary table generation.

Reusable proposal sentence:

> I have a small reference project that demonstrates a similar workflow: ingest messy CSV/API/Excel/JSON data, validate it with explicit schema rules, clean it, export a reporting-ready dataset to CSV, SQLite, PostgreSQL, or optional Parquet, and generate a clear data quality report.

## License

MIT
