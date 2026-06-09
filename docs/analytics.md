# v0.4 Analytics-ready Export Demo

v0.4.0 adds a larger generated data and analytics-ready export path to the existing data quality ETL starter.

The goal is not to turn this repository into a big data platform, BI dashboard, data warehouse, Airflow/dbt/Spark project, or AI application. The goal is to show a small, repeatable workflow that can handle more realistic synthetic customer/order-style data and produce files that are ready for local analysis.

```text
generated messy order data
→ existing validation and cleaning logic
→ cleaned CSV
→ cleaned Parquet
→ DuckDB SQL query demo
→ summary CSV tables
→ benchmark_report.md
```

## Scope

v0.4.0 keeps the existing workflows intact:

- v0.1 CLI workflow remains the source of truth.
- v0.2 optional PostgreSQL export remains available.
- v0.3 optional FastAPI validation service remains available.
- v0.4 analytics export is an optional demo path.

v0.4.0 intentionally does not add:

- user login
- frontend application
- async task queue
- cloud deployment
- BI dashboard
- Metabase
- data warehouse implementation
- Airflow
- dbt
- Spark
- SQLModel metadata layer
- AI / LLM / RAG / agent features

## Synthetic data note

The generated data is synthetic demo data. It is not real customer data and is not downloaded from an external dataset.

The generator creates deterministic customer/order-style rows with a fixed seed. It also introduces intentional data quality issues such as missing email values, invalid email values, missing country values, inconsistent country casing, duplicate rows, invalid dates, negative quantities, and zero prices.

Large generated files should not be committed to GitHub. The `.gitignore` file excludes:

```text
data/generated/
data/output/analytics/
*.parquet
```

## Install dependencies

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

The v0.4 analytics demo uses `pyarrow` for Parquet output and `duckdb` for querying the Parquet file locally.

## Generate synthetic order data

### 1,000 rows

macOS / Linux:

```bash
python scripts/generate_sample_data.py \
  --rows 1000 \
  --output data/generated/orders_1k.csv \
  --seed 42
```

Windows PowerShell:

```powershell
python scripts/generate_sample_data.py `
  --rows 1000 `
  --output data/generated/orders_1k.csv `
  --seed 42
```

### 10,000 rows

macOS / Linux:

```bash
python scripts/generate_sample_data.py \
  --rows 10000 \
  --output data/generated/orders_10k.csv \
  --seed 42
```

Windows PowerShell:

```powershell
python scripts/generate_sample_data.py `
  --rows 10000 `
  --output data/generated/orders_10k.csv `
  --seed 42
```

### 100,000 rows

macOS / Linux:

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

## Run the analytics demo

macOS / Linux:

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

## DuckDB query example

The demo writes reusable SQL to:

```text
data/output/analytics/analytics_queries.sql
```

Example query:

```sql
SELECT country, ROUND(SUM(revenue), 2) AS total_revenue, COUNT(*) AS order_count
FROM read_parquet('data/output/analytics/cleaned_orders.parquet')
GROUP BY country
ORDER BY total_revenue DESC
LIMIT 10;
```

The script also runs a small DuckDB preview query and prints the result in the terminal.

## Summary tables

The demo produces lightweight CSV summary tables:

- `customer_summary.csv`: one row per customer with order count, revenue, and first/last order dates.
- `revenue_by_country.csv`: country-level order count, customer count, total revenue, and average order value.
- `orders_by_month.csv`: monthly order count, customer count, and total revenue.
- `source_system_summary.csv`: order and revenue totals by source system.

These are reporting-ready artifacts, not a BI dashboard.

## Benchmark report

The benchmark report is written to:

```text
data/output/analytics/benchmark_report.md
```

It includes:

- input file path
- raw row count
- cleaned row count
- analytics-ready row count
- validation issue count
- runtime seconds
- output file paths and sizes
- DuckDB query preview
- scope note

This is a lightweight local benchmark, not a formal performance benchmark.

## Docker usage

The default Docker build and run should remain focused on the existing CLI demo:

```bash
docker build -t data-quality-etl-starter:0.4.0 -t data-quality-etl-starter:latest .
docker run --rm data-quality-etl-starter:0.4.0
```

To run the analytics demo in a container, mount the repository working directory and run the scripts manually after the image has dependencies installed. One simple local option is:

```bash
docker run --rm -v "$PWD:/app" -w /app data-quality-etl-starter:0.4.0 \
  python scripts/generate_sample_data.py \
  --rows 1000 \
  --output data/generated/orders_1k.csv \
  --seed 42
```

Then:

```bash
docker run --rm -v "$PWD:/app" -w /app data-quality-etl-starter:0.4.0 \
  python scripts/run_analytics_demo.py \
  --input data/generated/orders_1k.csv \
  --schema data/expected/generated_order_schema.json \
  --output-dir data/output/analytics
```

Windows PowerShell Docker volume paths may require `${PWD}`:

```powershell
docker run --rm -v ${PWD}:/app -w /app data-quality-etl-starter:0.4.0 `
  python scripts/generate_sample_data.py `
  --rows 1000 `
  --output data/generated/orders_1k.csv `
  --seed 42
```

## Validation commands

Run all tests:

```bash
python -m compileall -q src/dq_etl_starter
pytest
```

Run v0.4-specific tests:

```bash
pytest tests/test_generate_sample_data.py
pytest tests/test_analytics.py
pytest tests/test_exporters_parquet.py
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'dq_etl_starter'`

Install the package in editable mode from the repository root:

```bash
pip install -e .
```

### `ImportError` or `ModuleNotFoundError` for `pyarrow`

Install requirements again:

```bash
pip install -r requirements.txt
```

Parquet export uses pandas with the PyArrow engine available in the environment.

### `ModuleNotFoundError: No module named 'duckdb'`

Install requirements again:

```bash
pip install -r requirements.txt
```

DuckDB is used only for the optional analytics demo.

### Output directory is empty

Make sure the input file exists first:

```bash
python scripts/generate_sample_data.py --rows 1000 --output data/generated/orders_1k.csv --seed 42
```

Then run:

```bash
python scripts/run_analytics_demo.py --input data/generated/orders_1k.csv --schema data/expected/generated_order_schema.json --output-dir data/output/analytics
```

### Git shows generated files

The v0.4 `.gitignore` excludes large generated data and local analytics outputs. If files were already staged before updating `.gitignore`, unstage them:

```bash
git restore --staged data/generated data/output/analytics
```

## Positioning

This demo is useful for Upwork-style tasks such as:

- CSV cleanup for larger datasets
- Excel / CSV reporting data preparation
- generated test data for ETL validation
- analytics-ready CSV / Parquet export
- DuckDB local analytics demo
- customer/order data preparation
- summary table generation
- lightweight reporting data pipeline

It is intentionally small, local, testable, and reproducible.
