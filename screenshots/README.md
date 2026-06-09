# Screenshots

These screenshots support the project README, technical documentation, tutorials, and portfolio references.

The recommended story is:

1. raw messy data;
2. CLI workflow run;
3. generated data quality report;
4. cleaned reporting-ready output;
5. passing pytest tests;
6. Docker run;
7. nested JSON flattened into a table;
8. optional PostgreSQL export and table verification;
9. optional FastAPI Swagger UI;
10. `/validate` API response JSON;
11. generated 100k synthetic data;
12. analytics-ready output files and DuckDB query preview;
13. benchmark report.

## Current screenshots

| File                                        | Version | Purpose                                                                                                      |
| ------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------ |
| `01_raw_messy_data.png`                     | v0.1.0  | Shows the original messy CSV input.                                                                          |
| `02_cli_run.png`                            | v0.1.0  | Shows the CLI workflow running successfully.                                                                 |
| `03_quality_report.png`                     | v0.1.0  | Shows the generated Markdown data quality report.                                                            |
| `04_cleaned_output.png`                     | v0.1.0  | Shows the cleaned CSV output.                                                                                |
| `05_pytest_pass.png`                        | v0.1.0  | Shows the test suite passing.                                                                                |
| `06_docker_run.png`                         | v0.1.0  | Shows Docker build/run reproducibility.                                                                      |
| `07_json_flatten_output.png`                | v0.1.0  | Shows nested JSON flattened into tabular output.                                                             |
| `08_postgres_export.png`                    | v0.2.0  | Shows optional PostgreSQL export and table verification.                                                     |
| `09_fastapi_swagger.png`                    | v0.3.0  | Shows Swagger UI at `http://127.0.0.1:8000/docs` with `GET /health` and `POST /validate`.                    |
| `10_validate_response.png`                  | v0.3.0  | Shows a successful `/validate` response containing quality report JSON.                                      |
| `11_generated_data_100k.png`                | v0.4.0  | Shows `generate_sample_data.py` generating 100,000 synthetic rows.                                           |
| `12_analytics_outputs_and_duckdb_query.png` | v0.4.0  | Shows analytics output files and the DuckDB preview query result from the Parquet file.                      |
| `13_benchmark_report.png`                   | v0.4.0  | Shows the generated benchmark report with row counts, runtime, output files, DuckDB preview, and scope note. |

## Capture notes for v0.1.0

### `01_raw_messy_data.png`

Open:

```text
data/input/messy_customers.csv
```

Capture the raw input file showing typical data quality issues, such as:

* inconsistent column names;
* missing values;
* duplicate rows;
* invalid email values;
* inconsistent formatting.

### `02_cli_run.png`

Run the default CSV workflow:

```bash
python -m dq_etl_starter.cli run \
  --input data/input/messy_customers.csv \
  --input-type csv \
  --schema data/expected/customer_schema.json \
  --output-dir data/output/csv \
  --db-target sqlite \
  --table-name cleaned_customers
```

Capture the terminal output showing the CLI command completed successfully.

### `03_quality_report.png`

Open:

```text
data/output/csv/quality_report.md
```

Capture the generated Markdown report showing:

* row counts;
* column counts;
* missing values;
* duplicate rows;
* validation issues;
* warning messages.

### `04_cleaned_output.png`

Open:

```text
data/output/csv/cleaned_customers.csv
```

Capture the cleaned output file showing normalized columns and cleaned records.

### `05_pytest_pass.png`

Run:

```bash
pytest
```

Capture the terminal output showing the test suite passing.

### `06_docker_run.png`

Run:

```bash
docker build -t data-quality-etl-starter:latest .
docker run --rm data-quality-etl-starter:latest
```

Capture the terminal output showing Docker build/run reproducibility.

### `07_json_flatten_output.png`

Run the nested JSON workflow:

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

Capture the cleaned output or terminal result showing nested JSON flattened into a table.

## Capture notes for v0.2.0

### `08_postgres_export.png`

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Set `DATABASE_URL` and run the PostgreSQL export workflow:

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

Capture either:

* the terminal output showing PostgreSQL export success; or
* a SQL query result showing rows in the `cleaned_customers` table.

## Capture notes for v0.3.0

### `09_fastapi_swagger.png`

Start the API:

```bash
uvicorn dq_etl_starter.api:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Make sure the screenshot shows both:

* `GET /health`;
* `POST /validate`.

If local Windows port binding fails, the API can also be verified through Docker:

```bash
docker run --rm -p 8000:8000 data-quality-etl-starter:0.4.0 \
  uvicorn dq_etl_starter.api:app --host 0.0.0.0 --port 8000
```

Then open:

```text
http://127.0.0.1:8000/docs
```

### `10_validate_response.png`

Use Swagger UI to upload:

```text
file = data/input/messy_customers.csv
input_type = csv
schema_file = data/expected/customer_schema.json
save_report = false
```

Capture the response body showing fields such as:

* `dataset_name`;
* `row_count_raw`;
* `row_count_cleaned`;
* `missing_values_by_column`;
* `duplicate_row_count`;
* `issues`.

## Capture notes for v0.4.0

### `11_generated_data_100k.png`

Run:

```bash
python scripts/generate_sample_data.py \
  --rows 100000 \
  --output data/generated/orders_100k.csv \
  --seed 42
```

Windows PowerShell:

```powershell
python scripts/generate_sample_data.py `
  --rows 100000 `
  --output data/generated/orders_100k.csv `
  --seed 42
```

Capture the terminal output showing:

* `Rows: 100,000`;
* the seed;
* the output path;
* the synthetic data note.

### `12_analytics_outputs_and_duckdb_query.png`

Run the analytics demo:

```bash
python scripts/run_analytics_demo.py \
  --input data/generated/orders_100k.csv \
  --schema data/expected/generated_order_schema.json \
  --output-dir data/output/analytics
```

Windows PowerShell:

```powershell
python scripts/run_analytics_demo.py `
  --input data/generated/orders_100k.csv `
  --schema data/expected/generated_order_schema.json `
  --output-dir data/output/analytics
```

Capture the terminal output showing:

* the run summary;
* `cleaned_orders.csv`;
* `cleaned_orders.parquet`;
* `customer_summary.csv`;
* `revenue_by_country.csv`;
* `orders_by_month.csv`;
* `source_system_summary.csv`;
* `analytics_queries.sql`;
* `benchmark_report.md`;
* the `DuckDB preview query` section.

### `13_benchmark_report.png`

Open:

```text
data/output/analytics/benchmark_report.md
```

Capture the report showing:

* raw row count;
* cleaned row count;
* analytics-ready row count;
* validation issue count;
* runtime seconds;
* output file list;
* DuckDB preview;
* scope note.

## Notes

Generated data and analytics outputs are intentionally local artifacts.

Do not commit:

```text
data/generated/
data/output/analytics/
*.parquet
```

The repository should keep only source code, tests, documentation, lightweight sample files, and screenshots.
