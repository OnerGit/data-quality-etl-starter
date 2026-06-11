# Optional Metabase Local Demo

This document explains how to use Metabase as an optional local dashboard tool for the v0.5 BI-ready reporting demo.

Metabase is not required for the core CLI workflow, PostgreSQL export, FastAPI validation service, generated data workflow, or analytics-ready export.

This project does not configure Metabase for production, does not embed Metabase, and does not use Metabase as a custom frontend.

## Start PostgreSQL and Metabase

Start PostgreSQL first:

```bash
docker compose up -d postgres
```

Then start Metabase:

```bash
docker compose up -d metabase
```

Open:

```text
http://localhost:3000
```

The first-time setup is completed in the browser.

## Add PostgreSQL database in Metabase

When Metabase runs through Docker Compose, use these connection values:

| Field | Value |
|---|---|
| Database type | PostgreSQL |
| Host | postgres |
| Port | 5432 |
| Database name | dq_demo |
| Username | dq_user |
| Password | dq_password |

Use `postgres` because it is the Docker Compose service name. Use `localhost` only when connecting from your host machine.

## Recommended questions

Create simple questions from these views:

### Revenue by country

Source:

```text
vw_revenue_by_country
```

Suggested visualization:

```text
bar chart
```

### Orders by month

Source:

```text
vw_orders_by_month
```

Suggested visualization:

```text
line chart or table
```

### Monthly revenue trend

Source:

```text
vw_monthly_revenue_trend
```

Suggested visualization:

```text
line chart
```

### Orders by source system

Source:

```text
vw_source_system_quality
```

Suggested visualization:

```text
bar chart or table
```

### Average order value by country

Source:

```text
vw_revenue_by_country
```

Suggested visualization:

```text
bar chart
```

## Screenshot guidance

Recommended screenshots:

```text
screenshots/15_metabase_connection.png
screenshots/16_metabase_dashboard.png
```

The dashboard should stay simple. It only needs to show that cleaned and analytics-ready outputs can support lightweight BI/dashboard preparation.

Avoid screenshots that show:

- real customer data;
- non-demo credentials;
- local private paths;
- production configuration;
- dashboard exports with sensitive configuration.

## Stop services

Stop containers:

```bash
docker compose down
```

Remove local volumes if you want a clean reset:

```bash
docker compose down -v
```

## Scope note

This demo is intentionally local and optional. It is not a production BI platform, data warehouse, embedded analytics SDK, user-management system, or cloud deployment.
