# Screenshots

These screenshots are used to support the GitHub README, Dev.to article, Upwork portfolio entry, and proposal references.

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
12. analytics-ready output files;
13. DuckDB query result;
14. benchmark report.

## Current screenshots

| File | Version | Purpose |
|---|---|---|
| `01_raw_messy_data.png` | v0.1.0 | Shows the original messy CSV input. |
| `02_cli_run.png` | v0.1.0 | Shows the CLI workflow running successfully. |
| `03_quality_report.png` | v0.1.0 | Shows the generated Markdown data quality report. |
| `04_cleaned_output.png` | v0.1.0 | Shows the cleaned CSV output. |
| `05_pytest_pass.png` | v0.1.0 | Shows the test suite passing. |
| `06_docker_run.png` | v0.1.0 | Shows Docker build/run reproducibility. |
| `07_json_flatten_output.png` | v0.1.0 | Shows nested JSON flattened into tabular output. |
| `08_postgres_export.png` | v0.2.0 | Shows optional PostgreSQL export and table verification. |
| `09_fastapi_swagger.png` | v0.3.0 | Shows Swagger UI at `http://127.0.0.1:8000/docs` with `GET /health` and `POST /validate`. |
| `10_validate_response.png` | v0.3.0 | Shows a successful `/validate` response containing quality report JSON. |
| `11_generated_data_100k.png` | v0.4.0 | Shows `generate_sample_data.py` generating 100,000 synthetic rows. |
| `12_analytics_outputs.png` | v0.4.0 | Shows `data/output/analytics/` with cleaned CSV, Parquet, summaries, SQL, and benchmark report. |
| `13_duckdb_query.png` | v0.4.0 | Shows the DuckDB query preview against the Parquet file. |
| `14_benchmark_report.png` | v0.4.0 | Shows the generated benchmark report with row counts, runtime, and output files. |

## Capture notes for v0.3.0

For `09_fastapi_swagger.png`, start the API and open:

```text
http://127.0.0.1:8000/docs
```

Make sure the screenshot shows both:

- `GET /health`
- `POST /validate`

For `10_validate_response.png`, use Swagger UI to upload:

```text
file = data/input/messy_customers.csv
input_type = csv
schema_file = data/expected/customer_schema.json
save_report = false
```

Capture the response body showing fields such as:

- `dataset_name`
- `row_count_raw`
- `row_count_cleaned`
- `missing_values_by_column`
- `duplicate_row_count`
- `issues`

## Capture notes for v0.4.0

### `11_generated_data_100k.png`

Run:

```bash
python scripts/generate_sample_data.py --rows 100000 --output data/generated/orders_100k.csv --seed 42
```

Capture the terminal output showing:

- `Rows: 100,000`
- the seed
- the output path
- the synthetic data note

### `12_analytics_outputs.png`

Run the analytics demo:

```bash
python scripts/run_analytics_demo.py --input data/generated/orders_100k.csv --schema data/expected/generated_order_schema.json --output-dir data/output/analytics
```

Capture either terminal output or file explorer showing:

- `cleaned_orders.csv`
- `cleaned_orders.parquet`
- `customer_summary.csv`
- `revenue_by_country.csv`
- `orders_by_month.csv`
- `analytics_queries.sql`
- `benchmark_report.md`

### `13_duckdb_query.png`

Capture the `DuckDB preview` section printed by `scripts/run_analytics_demo.py`, or run a DuckDB query from `analytics_queries.sql`.

### `14_benchmark_report.png`

Open:

```text
data/output/analytics/benchmark_report.md
```

Capture the report showing:

- raw row count
- cleaned row count
- analytics-ready row count
- runtime seconds
- output file list
- scope note
