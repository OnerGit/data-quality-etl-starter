# Troubleshooting

## `ModuleNotFoundError: No module named 'dq_etl_starter'`

Run commands from the project root and install the project in editable mode:

```bash
pip install -r requirements.txt
pip install -e .
```

For temporary local testing, you can also set `PYTHONPATH`:

```bash
export PYTHONPATH=src
```

Windows PowerShell:

```powershell
$env:PYTHONPATH="src"
```

## Excel files cannot be read

Install `openpyxl`:

```bash
pip install openpyxl
```

The dependency is already listed in `requirements.txt`.

## Output files overwrite each other

If you run CSV, Excel, JSON, and mock API workflows into the same `data/output` folder, later runs can overwrite `quality_report.md` and `quality_report.json`.

Use separate output folders:

```bash
--output-dir data/output/csv
--output-dir data/output/excel
--output-dir data/output/json
--output-dir data/output/mock_api
```

## Validation report shows `Row 6` when the data has five rows

The validation report uses source file line numbers for CSV-style inputs.

For example:

```text
Line 1: header row
Line 2: first data row
Line 3: second data row
Line 4: third data row
Line 5: fourth data row
Line 6: fifth data row
```

So `Row 6` points to the fifth data record in the original source file.

## PostgreSQL export fails with missing `DATABASE_URL`

PostgreSQL is optional.

For the default v0.1 path, use SQLite:

```bash
--db-target sqlite
```

For PostgreSQL, start the local container and provide `DATABASE_URL`:

```bash
docker compose up -d postgres
```

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

## Docker build fails during `pip install`

If Docker fails during `pip install`, retry first. Slow or unstable networks can interrupt package downloads.

```bash
docker build --no-cache --progress=plain -t data-quality-etl-starter .
```

If the issue persists, clean the builder cache and rebuild:

```bash
docker builder prune
docker build --no-cache --progress=plain -t data-quality-etl-starter .
```

## Docker cannot write output files

Mount the output directory when running the container:

```bash
docker run --rm -v "${PWD}/data/output:/app/data/output" data-quality-etl-starter
```

Windows PowerShell:

```powershell
docker run --rm -v "${PWD}/data/output:/app/data/output" data-quality-etl-starter
```

## Validation report shows unexpected columns

This usually means the input data has columns that are not listed in the schema JSON file.

Update the schema if the column is legitimate, or clean the source file if the column is accidental.

## Date validation warnings appear

The starter uses pandas date parsing for flexible formats. If a date value is ambiguous or invalid, the workflow reports it instead of silently changing it.

## Bad email warnings appear

The email check is intentionally simple. It is designed to catch obvious issues in business spreadsheets, not to fully validate all possible email address edge cases.
