# Data Quality ETL Starter

Small teams often receive messy CSV, Excel, JSON, or API data before reporting. This project shows how to turn those inputs into a repeatable Python workflow that validates, cleans, exports, and documents the data quality of each run.

This is a practical GitHub portfolio project for lightweight data cleaning, validation, reporting automation, and ETL work. It is intentionally small enough to understand, run, test, and adapt.

## What problem this solves

Many small-team data problems are not big data problems. They are repeatability, validation, and handoff problems.

Typical issues include:

- messy CSV or Excel exports from different tools;
- inconsistent column names;
- missing values and duplicate rows;
- invalid email, date, or number formats;
- nested JSON that must become reporting-ready tables;
- manual Excel cleanup repeated every week;
- no data quality report for handoff.

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
- generate a Markdown and JSON data quality report;
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
export cleaned CSV + SQLite
        ↓
generate data quality report
```

## Tech stack

- Python
- pandas
- Pydantic
- SQLite
- SQLAlchemy-ready optional PostgreSQL export
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
├── src/dq_etl_starter/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Quick start

```bash
git clone https://github.com/<your-username>/data-quality-etl-starter.git
cd data-quality-etl-starter
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run with sample CSV

```bash
python -m dq_etl_starter.cli run   --input data/input/messy_customers.csv   --input-type csv   --schema data/expected/customer_schema.json   --output-dir data/output   --db-target sqlite   --table-name cleaned_customers
```

Expected outputs:

```text
data/output/cleaned_customers.csv
data/output/etl_output.sqlite
data/output/quality_report.md
data/output/quality_report.json
```

## Run with sample Excel

```bash
python -m dq_etl_starter.cli run   --input data/input/messy_orders.xlsx   --input-type excel   --schema data/expected/order_schema.json   --output-dir data/output   --db-target sqlite   --table-name cleaned_orders
```

## Run with nested JSON

```bash
python -m dq_etl_starter.cli run   --input data/input/nested_customers.json   --input-type json   --records-path data.customers   --schema data/expected/customer_schema.json   --output-dir data/output   --db-target sqlite   --table-name cleaned_customers_json
```

## Run with mock API data

This project does not call a real external API in v0.1. The mock API file simulates a JSON response so the workflow stays reproducible and does not require API keys.

```bash
python -m dq_etl_starter.cli run   --input data/input/mock_api_orders.json   --input-type mock-api   --records-path data.orders   --schema data/expected/order_schema.json   --output-dir data/output   --db-target sqlite   --table-name cleaned_api_orders
```

## Data quality report

The workflow generates a Markdown report with:

- raw row count;
- cleaned row count;
- column list;
- missing values by column;
- duplicate row count;
- missing expected columns;
- unexpected columns;
- validation issues;
- output files.

## Pydantic schema models

Pydantic is used for workflow and reporting contracts, not for hardcoding every dynamic business row.

Core models include:

- `WorkflowConfig`
- `DatasetSchema`
- `ColumnRule`
- `ValidationIssue`
- `QualityReport`

The cleaning itself remains DataFrame-based because freelance CSV, Excel, JSON, and API data often has changing columns.

## SQLite output

SQLite is the default database target because it is local, portable, and easy to inspect.

```bash
sqlite3 data/output/etl_output.sqlite
.tables
SELECT * FROM cleaned_customers LIMIT 5;
```

## Optional PostgreSQL output

PostgreSQL is an optional v0.2 target. It is useful when a client wants cleaned data loaded into a shared database instead of a local SQLite file.

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Run export:

```bash
DATABASE_URL=postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo python -m dq_etl_starter.cli run   --input data/input/messy_customers.csv   --input-type csv   --schema data/expected/customer_schema.json   --output-dir data/output   --db-target postgres   --table-name cleaned_customers
```

## Run tests

```bash
pytest
```

## Run with Docker

```bash
docker build -t data-quality-etl-starter .
docker run --rm -v "${PWD}/data/output:/app/data/output" data-quality-etl-starter
```

## Optional FastAPI layer

FastAPI is intentionally not part of the v0.1 core. The v0.3 layer can add endpoints such as:

- `GET /health`
- `POST /upload`
- `POST /validate`
- `GET /report/{run_id}`

The CLI workflow remains the source of truth.

## Screenshots

Recommended screenshot sequence:

1. raw messy data;
2. CLI run;
3. quality report;
4. cleaned output;
5. pytest pass;
6. Docker run;
7. optional PostgreSQL export;
8. optional Swagger UI;
9. optional `/validate` response.

See `docs/workflow.md` for the screenshot story.

## Troubleshooting

See `docs/troubleshooting.md`.

## What this project is not

This is not a big data platform, an Airflow/dbt project, or a production data warehouse. It is a small, practical starter for repeatable data cleaning, validation, export, and reporting workflows.

The goal is to demonstrate the kind of lightweight data workflow that many small teams need before they invest in heavier data infrastructure.

## How this maps to client work

This project maps to common freelance tasks such as:

- API to CSV workflows;
- CSV and Excel cleanup;
- JSON to CSV conversion;
- data validation and quality reporting;
- reporting automation;
- lightweight ETL;
- export to SQLite or PostgreSQL;
- preparing cleaner data for dashboards, analytics, or APIs.

## License

MIT
