# Screenshots

These screenshots support the project README, technical documentation, and tutorials.

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
13. benchmark report;
14. BI reporting tables and views;
15. Metabase PostgreSQL connection;
16. basic Metabase dashboard;
17. BI summary report;
18. AI-ready demo run;
19. AI-ready output files;
20. data dictionary JSON;
21. AI-ready summary report.

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
| `12_analytics_outputs_and_duckdb_query.png` | v0.4.0 | Shows analytics output files and the DuckDB preview query result from the Parquet file. |
| `13_benchmark_report.png` | v0.4.0 | Shows the generated benchmark report with row counts, runtime, output files, DuckDB preview, and scope note. |
| `14_bi_reporting_tables.png` | v0.5.0 | Shows PostgreSQL reporting tables and views created by the BI-ready demo. |
| `15_metabase_connection.png` | v0.5.0 | Shows Metabase connected to the local PostgreSQL reporting database. |
| `16_metabase_dashboard.png` | v0.5.0 | Shows a basic Metabase dashboard built from reporting views. |
| `17_bi_summary_report.png` | v0.5.0 | Shows the generated BI summary report with table counts, views, output files, and scope note. |
| `18_ai_ready_demo_run.png` | v0.6.0 | Shows `run_ai_ready_demo.py` completing successfully and confirming no LLM API call, no embeddings, and no model training. |
| `19_ai_ready_outputs.png` | v0.6.0 | Shows the generated files under `data/output/ai_ready/`. |
| `20_data_dictionary_json.png` | v0.6.0 | Shows `data_dictionary.json` with dataset name, columns, descriptions, roles, nullable flags, and example values. |
| `21_ai_ready_summary_report.png` | v0.6.0 | Shows the generated AI-ready summary report with output files, scope note, and downstream-use guidance. |

## Capture notes for v0.6.0

### `18_ai_ready_demo_run.png`

Generate data first:

```powershell
python scripts/generate_sample_data.py `
  --rows 100000 `
  --output data/generated/orders_100k.csv `
  --seed 42
```

Run:

```powershell
python scripts/run_ai_ready_demo.py `
  --input data/generated/orders_100k.csv `
  --schema data/expected/generated_order_schema.json `
  --output-dir data/output/ai_ready `
  --dataset-name synthetic_orders
```

Capture the terminal output showing:

- the input file;
- the output directory;
- the generated output files;
- `No LLM API was called.`;
- `No embeddings were generated.`;
- `No model was trained.`.

### `19_ai_ready_outputs.png`

Open or list:

```powershell
Get-ChildItem data/output/ai_ready
```

Capture the output directory showing:

- `schema_profile.json`;
- `data_dictionary.json`;
- `validation_summary.json`;
- `feature_ready_orders.csv`;
- `embedding_ready_text_fields.csv`;
- `ai_ready_manifest.json`;
- `ai_ready_summary_report.md`.

### `20_data_dictionary_json.png`

Open:

```text
data/output/ai_ready/data_dictionary.json
```

Capture the top portion showing:

- `dataset_name`;
- `description`;
- `columns`;
- column `name`;
- column `description`;
- `role`;
- `nullable`;
- `example_values`.

Do not capture any real sensitive data. The default v0.6 workflow uses synthetic generated data.

### `21_ai_ready_summary_report.png`

Open:

```text
data/output/ai_ready/ai_ready_summary_report.md
```

Capture the Markdown preview or editor view showing:

- generated outputs;
- scope note;
- no LLM API call;
- no embeddings generated;
- no model trained;
- recommended downstream use.

## Screenshot policy

Screenshots should demonstrate the workflow without exposing secrets, private data, real customer data, API keys, database passwords, or local personal paths.

The repository should not commit generated raw data or local output folders. Screenshots are acceptable when they only show synthetic demo data, terminal output, documentation, or local demo metadata.
