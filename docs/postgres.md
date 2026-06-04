# Optional PostgreSQL Export

PostgreSQL is an optional v0.2 export target.

SQLite remains the default local database target because it is portable, serverless, and easy to inspect. PostgreSQL is useful when a client wants cleaned CSV, Excel, JSON, or API-style data loaded into a more realistic reporting database.

This project is still a small data quality ETL starter. It is not a production data warehouse.

---

## What this workflow does

Default path:

```text
CSV / Excel / JSON / mock API
→ read / flatten
→ normalize columns
→ validate
→ clean
→ cleaned CSV
→ SQLite
→ Markdown / JSON quality report
```

Optional PostgreSQL path:

```text
CSV / Excel / JSON / mock API
→ read / flatten
→ normalize columns
→ validate
→ clean
→ cleaned CSV
→ PostgreSQL
→ Markdown / JSON quality report
```

---

## Start local PostgreSQL

This project uses Docker Compose for the local PostgreSQL demo.

```bash
docker compose up -d postgres
```

Check the service status:

```bash
docker compose ps
```

The compose file starts a local PostgreSQL container with demo credentials:

```text
POSTGRES_USER=dq_user
POSTGRES_PASSWORD=dq_password
POSTGRES_DB=dq_demo
```

These credentials are for local demo use only. Do not use the demo password in production.

---

## Set DATABASE_URL

The PostgreSQL export uses `DATABASE_URL`.

### Windows PowerShell

```powershell
$env:DATABASE_URL="postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo"

echo $env:DATABASE_URL
```

### macOS / Linux

```bash
export DATABASE_URL="postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo"

echo $DATABASE_URL
```

---

## Run the workflow with PostgreSQL

### Windows PowerShell

```powershell
python -m dq_etl_starter.cli run `
  --input data/input/messy_customers.csv `
  --input-type csv `
  --schema data/expected/customer_schema.json `
  --output-dir data/output/postgres `
  --db-target postgres `
  --table-name cleaned_customers
```

Expected terminal output includes:

```text
Data quality ETL workflow completed.
Database target: postgres
Database output: postgresql table: cleaned_customers
```

### macOS / Linux

```bash
python -m dq_etl_starter.cli run \
  --input data/input/messy_customers.csv \
  --input-type csv \
  --schema data/expected/customer_schema.json \
  --output-dir data/output/postgres \
  --db-target postgres \
  --table-name cleaned_customers
```

You can also pass the database URL directly:

```bash
python -m dq_etl_starter.cli run \
  --input data/input/messy_customers.csv \
  --input-type csv \
  --schema data/expected/customer_schema.json \
  --output-dir data/output/postgres \
  --db-target postgres \
  --table-name cleaned_customers \
  --database-url postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo
```

---

## Verify the PostgreSQL table

You do not need to install PostgreSQL locally. You can use `psql` inside the container:

```bash
docker exec -it dq_etl_postgres psql -U dq_user -d dq_demo -c "SELECT * FROM cleaned_customers LIMIT 5;"
```

Check row count:

```bash
docker exec -it dq_etl_postgres psql -U dq_user -d dq_demo -c "SELECT COUNT(*) FROM cleaned_customers;"
```

List tables:

```bash
docker exec -it dq_etl_postgres psql -U dq_user -d dq_demo -c "\dt"
```

---

## Run the default SQLite workflow

SQLite remains the default path:

```bash
python -m dq_etl_starter.cli run \
  --input data/input/messy_customers.csv \
  --input-type csv \
  --schema data/expected/customer_schema.json \
  --output-dir data/output/csv \
  --db-target sqlite \
  --table-name cleaned_customers
```

Expected SQLite output:

```text
data/output/csv/etl_output.sqlite
```

---

## Optional PostgreSQL integration test

The PostgreSQL integration test is designed to skip automatically when `DATABASE_URL` is not set.

Default tests:

```bash
pytest
```

Run integration tests explicitly after starting PostgreSQL and setting `DATABASE_URL`:

```bash
pytest -m integration
```

---

## Troubleshooting

### DATABASE_URL is required

If you see:

```text
DATABASE_URL is required when db_target='postgres'
```

Set the environment variable first.

Windows PowerShell:

```powershell
$env:DATABASE_URL="postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo"
```

macOS / Linux:

```bash
export DATABASE_URL="postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo"
```

---

### Connection refused

If PostgreSQL export fails with a connection error, make sure the container is running:

```bash
docker compose up -d postgres
docker compose ps
```

Check logs:

```bash
docker compose logs postgres
```

---

### Password authentication failed

Make sure these values match across `docker-compose.yml` and `DATABASE_URL`:

```text
POSTGRES_USER=dq_user
POSTGRES_PASSWORD=dq_password
POSTGRES_DB=dq_demo
```

Connection URL:

```text
postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo
```

---

### Old credentials are still used

PostgreSQL initializes credentials when the data directory is first created. If you changed credentials after the volume was already created, remove the old volume and restart:

```bash
docker compose down -v
docker compose up -d postgres
```

This deletes the local demo database volume.

---

### Table does not exist

If this query fails:

```bash
docker exec -it dq_etl_postgres psql -U dq_user -d dq_demo -c "SELECT * FROM cleaned_customers LIMIT 5;"
```

Run the CLI workflow again with:

```bash
--db-target postgres
--table-name cleaned_customers
```

---

## Stop PostgreSQL

Stop the container but keep the data volume:

```bash
docker compose down
```

Stop the container and remove the local database volume:

```bash
docker compose down -v
```

Use `down -v` only when you want to reset the local demo database.

---

## Scope boundary

v0.2 only adds optional PostgreSQL export.

Intentionally out of scope:

- FastAPI
- SQLModel
- BI dashboard
- data warehouse
- Parquet
- DuckDB
- Airflow
- dbt
- LLM / RAG / Agent features