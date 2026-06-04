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
- generate Markdown and JSON data quality reports;
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
  --input data/input/nested_customers.json \
  --input-type json \
  --records-path data.customers \
  --schema data/expected/customer_schema.json \
  --output-dir data/output/json \
  --db-target sqlite \
  --table-name cleaned_customers_json
```

## Run with mock API data

This project does not call a real external API in v0.1. The mock API file simulates a JSON response so the workflow stays reproducible and does not require API keys.

```bash
python -m dq_etl_starter.cli run \
  --input data/input/mock_api_orders.json \
  --input-type mock-api \
  --records-path data.orders \
  --schema data/expected/order_schema.json \
  --output-dir data/output/mock_api \
  --db-target sqlite \
  --table-name cleaned_api_orders
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

The `Row` value in the validation report refers to the source file line number for CSV-style inputs. This includes the header row. For example, if the raw CSV has one header line and five data rows, a warning on `Row 6` points to the fifth data record in the source file.

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
sqlite3 data/output/csv/etl_output.sqlite
.tables
SELECT * FROM cleaned_customers LIMIT 5;
```

## Optional PostgreSQL output

SQLite remains the default database target. v0.2.0 adds an optional PostgreSQL export path for users who want a more realistic client-style database loading workflow.

This is useful for tasks such as:

- CSV to PostgreSQL;
- API-style JSON to PostgreSQL;
- Excel cleanup before database import;
- validation before loading data into a reporting database;
- lightweight ETL automation for small teams.

Start local PostgreSQL:

```bash
docker compose up -d postgres
```

Set `DATABASE_URL`.

Windows PowerShell:

```powershell
$env:DATABASE_URL="postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo"
```

macOS / Linux:

```bash
export DATABASE_URL="postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo"
```

Run export:

```bash
python -m dq_etl_starter.cli run \
  --input data/input/messy_customers.csv \
  --input-type csv \
  --schema data/expected/customer_schema.json \
  --output-dir data/output/postgres \
  --db-target postgres \
  --table-name cleaned_customers
```

Verify the table without installing PostgreSQL locally:

```bash
docker exec -it dq_etl_postgres psql -U dq_user -d dq_demo -c "SELECT * FROM cleaned_customers LIMIT 5;"
```

See [Optional PostgreSQL export](docs/postgres.md) for the full workflow.

## Run tests

```bash
pytest
```

## Run with Docker

```bash
docker build -t data-quality-etl-starter .
docker run --rm -v "${PWD}/data/output:/app/data/output" data-quality-etl-starter
```

On Windows PowerShell, use the same command:

```powershell
docker run --rm -v "${PWD}/data/output:/app/data/output" data-quality-etl-starter
```

## Screenshots

### Raw messy data

![Raw messy data](screenshots/01_raw_messy_data.png)

### CLI workflow run

![CLI run](screenshots/02_cli_run.png)

### Data quality report

![Quality report](screenshots/03_quality_report.png)

### Cleaned output

![Cleaned output](screenshots/04_cleaned_output.png)

### Passing tests

![Pytest pass](screenshots/05_pytest_pass.png)

### Docker run

![Docker run](screenshots/06_docker_run.png)

### Nested JSON flattened output

![JSON flatten output](screenshots/07_json_flatten_output.png)

### Optional PostgreSQL export

![PostgreSQL export](screenshots/08_postgres_export.png)

## Optional FastAPI layer

FastAPI is intentionally not part of the v0.1 core. A later v0.3 layer can add endpoints such as:

- `GET /health`
- `POST /upload`
- `POST /validate`
- `GET /report/{run_id}`

The CLI workflow remains the source of truth.

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

## Documentation

- [Workflow notes](docs/workflow.md)
- [Pydantic schema design](docs/pydantic-schema.md)
- [Optional PostgreSQL export](docs/postgres.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Upwork portfolio note](docs/upwork-portfolio-note.md)

## Related article

[Build a Python Data Quality ETL Starter for Messy CSV, Excel, JSON, and API-Style Data](https://dev.to/bob_oner/build-a-python-data-quality-etl-starter-for-messy-csv-excel-json-and-api-style-data-46b)

## License

MIT
