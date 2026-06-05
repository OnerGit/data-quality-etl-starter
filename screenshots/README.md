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
10. `/validate` API response JSON.

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
