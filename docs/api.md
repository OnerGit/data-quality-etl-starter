# Optional FastAPI Validation Service

v0.3.0 adds a small FastAPI validation service layer around the existing data quality workflow.

The CLI remains the source of truth. The API does not reimplement the ETL logic. It accepts uploaded CSV, Excel, or JSON files, reuses the same reader, validation, cleaning, and report-building modules, and returns a structured Pydantic-based quality report JSON.

## What this API layer does

The API is intended for lightweight internal validation demos and Upwork portfolio references.

It supports:

- `GET /health`
- `POST /validate`
- file upload through `multipart/form-data`
- CSV, Excel, and JSON input files
- uploaded JSON schema files
- optional `records_path` for nested JSON
- optional report saving under `data/output/api_runs/`
- Swagger UI at `/docs`

It intentionally does not include user login, a frontend, async queues, multi-tenant storage, cloud deployment, BI dashboards, SQLModel metadata tables, or AI/LLM features.

## Install dependencies

From the repository root:

```bash
pip install -r requirements.txt
pip install -e .
```

The editable install is recommended because the project uses a `src/` layout.

## Start the API locally

Windows PowerShell:

```powershell
uvicorn dq_etl_starter.api:app --reload --host 127.0.0.1 --port 8000
```

macOS / Linux:

```bash
uvicorn dq_etl_starter.api:app --reload --host 127.0.0.1 --port 8000
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Health check

Browser:

```text
http://127.0.0.1:8000/health
```

PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

macOS / Linux:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "data-quality-etl-starter-api",
  "version": "0.3.0"
}
```

## Validate a CSV file through Swagger UI

1. Start the API.
2. Open `http://127.0.0.1:8000/docs`.
3. Expand `POST /validate`.
4. Click **Try it out**.
5. Upload a CSV file, for example:
   - `data/input/messy_customers.csv`
6. Set `input_type` to:
   - `csv`
7. Upload a schema file, for example:
   - `data/expected/customer_schema.json`
8. Leave `records_path` empty for CSV or Excel files.
9. Keep `save_report` as `false` for a pure validation response.
10. Click **Execute**.

The response is a structured quality report JSON with fields such as:

- `dataset_name`
- `input_type`
- `row_count_raw`
- `row_count_cleaned`
- `column_count`
- `column_names`
- `expected_columns`
- `missing_expected_columns`
- `unexpected_columns`
- `missing_values_by_column`
- `duplicate_row_count`
- `issues`
- `output_files`

## Validate Excel

Use the same Swagger UI flow, but upload an Excel file and set:

```text
input_type = excel
```

Example files:

```text
data/input/messy_orders.xlsx
data/expected/order_schema.json
```

## Validate nested JSON

For nested JSON, upload the JSON file and schema file, then set `records_path`.

Example:

```text
file = data/input/nested_customers.json
input_type = json
schema_file = data/expected/customer_schema.json
records_path = data.customers
```

For mock API-style JSON, the CLI still supports `mock-api`. The v0.3 API keeps `/validate` limited to uploaded `csv`, `excel`, and `json` files to avoid turning the service layer into a broader backend system.

## Optional report saving

By default, `POST /validate` returns the report JSON without writing cleaned data or exporting to a database.

Set:

```text
save_report = true
```

Then the API writes report files under:

```text
data/output/api_runs/{run_id}/
```

This is only a local demo convenience. It is not a production report storage system.

## curl examples

macOS / Linux:

```bash
curl -X POST "http://127.0.0.1:8000/validate" \
  -F "file=@data/input/messy_customers.csv" \
  -F "input_type=csv" \
  -F "schema_file=@data/expected/customer_schema.json" \
  -F "save_report=false"
```

Nested JSON:

```bash
curl -X POST "http://127.0.0.1:8000/validate" \
  -F "file=@data/input/nested_customers.json" \
  -F "input_type=json" \
  -F "schema_file=@data/expected/customer_schema.json" \
  -F "records_path=data.customers" \
  -F "save_report=false"
```

PowerShell multipart `curl` syntax can be inconsistent because `curl` may map to `Invoke-WebRequest`. For Windows users, Swagger UI is the recommended validation path.

## Docker API run

Build the image:

```bash
docker build -t data-quality-etl-starter .
```

Run the API by overriding the default CLI command:

macOS / Linux:

```bash
docker run --rm -p 8000:8000 data-quality-etl-starter \
  uvicorn dq_etl_starter.api:app --host 0.0.0.0 --port 8000
```

Windows PowerShell:

```powershell
docker run --rm -p 8000:8000 data-quality-etl-starter `
  uvicorn dq_etl_starter.api:app --host 0.0.0.0 --port 8000
```

Open:

```text
http://127.0.0.1:8000/docs
```

The Dockerfile keeps the default CLI command unchanged. This preserves the original v0.1/v0.2 Docker workflow while allowing the v0.3 API service to be started explicitly.

## Tests

Run the full test suite:

```bash
pytest
```

Run only API tests:

```bash
pytest tests/test_api.py
```

The API tests use FastAPI `TestClient`, so they do not require starting a real web server and do not depend on PostgreSQL.

## Common errors

### `schema_file is required`

Upload the JSON schema file in the `schema_file` field. The API does not infer schema rules from the input file.

### `Unsupported input_type`

Use one of:

```text
csv
excel
json
```

The CLI still supports `mock-api`, but `/validate` is intentionally limited to uploaded file types.

### Nested JSON cannot find records path

Check that `records_path` matches the JSON structure.

For example, if the payload looks like this:

```json
{
  "data": {
    "customers": []
  }
}
```

Use:

```text
data.customers
```

### Swagger UI opens but `/validate` fails

Check:

- the API was started from the repository root;
- dependencies were installed with `pip install -r requirements.txt`;
- the uploaded schema file is valid JSON;
- the schema expected columns match the normalized column names;
- the selected `input_type` matches the uploaded file.

## Scope boundary

This service layer is intentionally small. It is not a production backend, a file management platform, a report database, a frontend app, an async job system, a warehouse, a BI stack, or an AI workflow.

The purpose is to demonstrate that the same repeatable CLI data cleaning and validation workflow can also be exposed as a lightweight HTTP validation service.
