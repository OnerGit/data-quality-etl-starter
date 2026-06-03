# Troubleshooting

## `ModuleNotFoundError: No module named 'dq_etl_starter'`

Run commands from the project root and install the project dependencies first.

```bash
pip install -r requirements.txt
```

For local development, you can also set `PYTHONPATH`:

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

## PostgreSQL export fails with missing `DATABASE_URL`

PostgreSQL is optional. For the default v0.1 path, use SQLite:

```bash
--db-target sqlite
```

For PostgreSQL, start the local container and provide `DATABASE_URL`:

```bash
docker compose up -d postgres
```

```bash
DATABASE_URL=postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo python -m dq_etl_starter.cli run   --input data/input/messy_customers.csv   --input-type csv   --schema data/expected/customer_schema.json   --output-dir data/output   --db-target postgres   --table-name cleaned_customers
```

## Docker cannot write output files

Mount the output directory when running the container:

```bash
docker run --rm -v "${PWD}/data/output:/app/data/output" data-quality-etl-starter
```

On Windows PowerShell:

```powershell
docker run --rm -v "${PWD}/data/output:/app/data/output" data-quality-etl-starter
```

## Validation report shows unexpected columns

This usually means the input data has columns that are not listed in the schema JSON file. Update the schema if the column is legitimate, or clean the source file if the column is accidental.

## Date validation warnings appear

The starter uses pandas date parsing for flexible formats. If a date value is ambiguous or invalid, the workflow reports it instead of silently changing it.

## Bad email warnings appear

The email check is intentionally simple. It is designed to catch obvious issues in business spreadsheets, not to fully validate all possible email address edge cases.
