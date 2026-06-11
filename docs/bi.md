# BI-ready Optional Demo

v0.5.0 adds an optional BI-ready reporting demo.

The purpose is to show that cleaned and analytics-ready outputs from this workflow can support lightweight reporting and dashboard preparation.

This is not a production BI platform, data warehouse, Metabase production deployment, embedded analytics setup, custom dashboard frontend, cloud deployment, or AI/LLM feature.

## Workflow

```text
generated messy order data
↓
existing validation and cleaning workflow
↓
analytics-ready order rows
↓
PostgreSQL reporting tables
↓
lightweight SQL views
↓
optional Metabase local dashboard demo
```

## What this demo creates

PostgreSQL reporting tables:

- `cleaned_orders`
- `customer_summary`
- `revenue_by_country`
- `orders_by_month`
- `source_system_summary`

PostgreSQL reporting views:

- `vw_revenue_by_country`
- `vw_orders_by_month`
- `vw_source_system_quality`
- `vw_monthly_revenue_trend`

Local output files:

```text
data/output/bi/bi_summary_report.md
data/output/bi/reporting_queries.sql
data/output/bi/metabase_dashboard_notes.md
```

The `data/output/bi/` directory is intentionally ignored by Git.

## Prerequisites

Install dependencies and the local package:

```bash
pip install -r requirements.txt
pip install -e .
```

The editable install step is recommended because the source code uses a `src/` layout.

## Step 1: Generate synthetic order data

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

This data is synthetic and should not be treated as real customer data.

## Step 2: Start PostgreSQL

```bash
docker compose up -d postgres
```

Check the container:

```bash
docker compose ps
```

## Step 3: Run the BI demo

macOS / Linux:

```bash
python scripts/run_bi_demo.py \
  --input data/generated/orders_100k.csv \
  --schema data/expected/generated_order_schema.json \
  --output-dir data/output/bi \
  --db-url postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo
```

Windows PowerShell:

```powershell
python scripts/run_bi_demo.py `
  --input data/generated/orders_100k.csv `
  --schema data/expected/generated_order_schema.json `
  --output-dir data/output/bi `
  --db-url postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo
```

Expected terminal sections:

- run summary;
- reporting tables;
- reporting views;
- BI output files.

## Step 4: Check reporting tables and views

List reporting tables and views:

```bash
docker exec -it dq_etl_postgres psql -U dq_user -d dq_demo -c "\dt"
docker exec -it dq_etl_postgres psql -U dq_user -d dq_demo -c "\dv"
```

Preview a reporting view:

```bash
docker exec -it dq_etl_postgres psql -U dq_user -d dq_demo -c "SELECT * FROM vw_revenue_by_country LIMIT 10;"
```

Preview the monthly trend view:

```bash
docker exec -it dq_etl_postgres psql -U dq_user -d dq_demo -c "SELECT * FROM vw_monthly_revenue_trend ORDER BY order_month LIMIT 12;"
```

## Step 5: Start optional Metabase

```bash
docker compose up -d metabase
```

Open:

```text
http://localhost:3000
```

The first-time setup happens in the browser. This local demo does not configure Metabase for production.

## Step 6: Connect Metabase to PostgreSQL

When Metabase runs through Docker Compose, use the Compose service name as the host:

| Field | Value |
|---|---|
| Database type | PostgreSQL |
| Host | postgres |
| Port | 5432 |
| Database name | dq_demo |
| Username | dq_user |
| Password | dq_password |

If you connect from a host-machine tool such as psql or a desktop database client, use `localhost` as the host.

## Recommended dashboard cards

Create basic cards from the reporting views:

- Revenue by country: `vw_revenue_by_country`
- Orders by month: `vw_orders_by_month`
- Monthly revenue trend: `vw_monthly_revenue_trend`
- Orders by source system: `vw_source_system_quality`
- Average order value by country: `vw_revenue_by_country`

Recommended chart choices:

- bar chart for revenue by country;
- line chart for monthly revenue trend;
- table or bar chart for source system summary.

## Recommended screenshots

Add these screenshots after running the local demo:

```text
screenshots/14_bi_reporting_tables.png
screenshots/15_metabase_connection.png
screenshots/16_metabase_dashboard.png
screenshots/17_bi_summary_report.png
```

Recommended capture content:

- `14_bi_reporting_tables.png`: terminal or psql output showing reporting tables and views;
- `15_metabase_connection.png`: successful Metabase PostgreSQL connection screen;
- `16_metabase_dashboard.png`: simple dashboard with revenue by country, orders by month, and source system summary;
- `17_bi_summary_report.png`: generated `bi_summary_report.md`.

Do not expose real credentials or sensitive data. Demo credentials are acceptable for the local demo, but password fields can still be visually masked.

## Common troubleshooting

### PostgreSQL is not ready

Run:

```bash
docker compose ps
```

If PostgreSQL is still starting, wait until the healthcheck passes.

### `psycopg` is missing

Install dependencies again:

```bash
pip install -r requirements.txt
```

### Metabase cannot connect to PostgreSQL

If Metabase runs inside Docker Compose, use:

```text
Host: postgres
```

Do not use `localhost` inside the Metabase container.

### Port 5432 or 3000 is already in use

Stop the conflicting local service or change the exposed port in `docker-compose.yml`.

### Old demo tables are still visible

The demo replaces reporting tables by default. To reset everything, remove local Docker volumes:

```bash
docker compose down -v
```

Then rerun the PostgreSQL and BI demo steps.

## Stop local services

Stop containers but keep volumes:

```bash
docker compose down
```

Stop containers and remove local volumes:

```bash
docker compose down -v
```

## Local artifact policy

Do not commit:

```text
data/generated/
data/output/analytics/
data/output/bi/
*.parquet
*.duckdb
metabase.db/
metabase-data/
postgres_data/
```

The repository should keep source code, tests, documentation, SQL templates, lightweight sample files, and screenshots.

## Real public dataset note

The v0.5.0 release should use synthetic generated data as the default BI demo input.

Real public data can be used for optional local validation, but do not commit large raw datasets or make default tests depend on external downloads. If a real dataset is used later, document the source, access note, license note, row count, schema mapping, validation issues, cleaning steps, reporting outputs, and limitations.
