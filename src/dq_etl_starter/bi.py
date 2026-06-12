from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import make_url

from dq_etl_starter.analytics import (
    build_customer_summary,
    build_orders_by_month,
    build_revenue_by_country,
    build_source_system_summary,
)
from dq_etl_starter.db import create_db_engine

REPORTING_TABLE_NAMES = [
    "cleaned_orders",
    "customer_summary",
    "revenue_by_country",
    "orders_by_month",
    "source_system_summary",
]

REPORTING_VIEW_NAMES = [
    "vw_revenue_by_country",
    "vw_orders_by_month",
    "vw_source_system_quality",
    "vw_monthly_revenue_trend",
]


def _safe_file_size(path: str | Path) -> int:
    file_path = Path(path)
    return file_path.stat().st_size if file_path.exists() and file_path.is_file() else 0


def _safe_database_url(database_url: str) -> str:
    """Return a display-safe database URL with the password hidden."""
    try:
        return make_url(database_url).render_as_string(hide_password=True)
    except Exception:
        return "<database-url-hidden>"


def _dataframe_to_markdown(df: pd.DataFrame, *, max_rows: int = 10) -> str:
    """Render a small DataFrame as Markdown without requiring tabulate."""
    if df.empty:
        return ""

    preview = df.head(max_rows)
    columns = [str(column) for column in preview.columns]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _index, row in preview.iterrows():
        values = [str(row[column]) for column in preview.columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _quote_identifier(identifier: str) -> str:
    """Quote a PostgreSQL identifier from the local reporting table allowlist."""
    return '"' + identifier.replace('"', '""') + '"'


def _truncate_table_if_exists(connection: Any, table_name: str) -> bool:
    """Truncate a PostgreSQL reporting table if it already exists.

    This keeps the table object intact, so dependent reporting views and local
    BI tools such as Metabase can keep referencing the same table and view
    names across repeated demo runs.
    """
    table_exists = connection.execute(
        text("SELECT to_regclass(:table_name)"),
        {"table_name": table_name},
    ).scalar()

    if table_exists is None:
        return False

    connection.execute(text(f"TRUNCATE TABLE {_quote_identifier(table_name)}"))
    return True


def build_reporting_tables(cleaned_orders: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Build BI-ready reporting tables from cleaned analytics-ready orders.

    These are lightweight reporting tables for local dashboard preparation.
    They are intentionally not a production warehouse model.
    """
    return {
        "cleaned_orders": cleaned_orders.copy(),
        "customer_summary": build_customer_summary(cleaned_orders),
        "revenue_by_country": build_revenue_by_country(cleaned_orders),
        "orders_by_month": build_orders_by_month(cleaned_orders),
        "source_system_summary": build_source_system_summary(cleaned_orders),
    }


def export_reporting_tables_to_postgres(
    tables: dict[str, pd.DataFrame],
    database_url: str,
    *,
    if_exists: str = "replace",
    chunksize: int = 1000,
) -> dict[str, int]:
    """Export reporting tables to a local PostgreSQL reporting database.

    The default demo behavior keeps repeated local runs stable without dropping
    existing reporting tables. When a reporting table already exists, it is
    truncated and repopulated instead of dropped and recreated. This preserves
    dependent reporting views and local Metabase dashboard references.
    """
    engine = create_db_engine(db_target="postgres", database_url=database_url)
    row_counts: dict[str, int] = {}

    try:
        with engine.begin() as connection:
            for table_name, df in tables.items():
                if table_name not in REPORTING_TABLE_NAMES:
                    raise ValueError(f"Unsupported reporting table: {table_name}")

                sql_if_exists = if_exists
                if if_exists == "replace":
                    table_existed = _truncate_table_if_exists(connection, table_name)
                    sql_if_exists = "append" if table_existed else "fail"

                df.to_sql(
                    table_name,
                    con=connection,
                    if_exists=sql_if_exists,
                    index=False,
                    method="multi",
                    chunksize=chunksize,
                )
                row_counts[table_name] = len(df)
    finally:
        engine.dispose()

    return row_counts


def build_reporting_views_sql() -> str:
    """Return PostgreSQL SQL for lightweight reporting views."""
    return """
CREATE OR REPLACE VIEW vw_revenue_by_country AS
SELECT
    country,
    order_count,
    customer_count,
    total_revenue,
    average_order_value
FROM revenue_by_country;

CREATE OR REPLACE VIEW vw_orders_by_month AS
SELECT
    order_month,
    order_count,
    customer_count,
    total_revenue
FROM orders_by_month;

CREATE OR REPLACE VIEW vw_source_system_quality AS
SELECT
    source_system,
    order_count,
    total_revenue
FROM source_system_summary;

CREATE OR REPLACE VIEW vw_monthly_revenue_trend AS
SELECT
    order_month,
    order_count,
    customer_count,
    total_revenue,
    ROUND((total_revenue::numeric / NULLIF(order_count, 0)), 2) AS average_order_value
FROM orders_by_month;
""".strip()


def create_reporting_views(database_url: str) -> list[str]:
    """Create lightweight PostgreSQL reporting views for the BI demo."""
    engine = create_db_engine(db_target="postgres", database_url=database_url)
    statements = [
        statement.strip()
        for statement in build_reporting_views_sql().split(";")
        if statement.strip()
    ]

    try:
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))
    finally:
        engine.dispose()

    return REPORTING_VIEW_NAMES.copy()


def build_dashboard_query_examples() -> str:
    """Return SQL examples for basic dashboard cards."""
    return """
-- Revenue by country
SELECT *
FROM vw_revenue_by_country
ORDER BY total_revenue DESC;

-- Orders by month
SELECT *
FROM vw_orders_by_month
ORDER BY order_month;

-- Monthly revenue trend
SELECT *
FROM vw_monthly_revenue_trend
ORDER BY order_month;

-- Orders by source system
SELECT *
FROM vw_source_system_quality
ORDER BY order_count DESC;

-- Average order value by country
SELECT
    country,
    average_order_value,
    order_count,
    total_revenue
FROM vw_revenue_by_country
ORDER BY average_order_value DESC;
""".strip()


def build_reporting_queries_sql() -> str:
    """Return a SQL file body containing view DDL and dashboard query examples."""
    return (
        "-- v0.5 BI-ready reporting SQL\n"
        "-- These queries are intended for a local PostgreSQL reporting database.\n"
        "-- This is not a production warehouse model.\n\n"
        "-- Reporting views\n"
        f"{build_reporting_views_sql()}\n\n"
        "-- Recommended dashboard card queries\n"
        f"{build_dashboard_query_examples()}\n"
    )


def write_reporting_queries(output_dir: str | Path) -> Path:
    """Write reporting view SQL and dashboard query examples."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "reporting_queries.sql"
    output_path.write_text(build_reporting_queries_sql(), encoding="utf-8")
    return output_path


def write_metabase_dashboard_notes(output_dir: str | Path) -> Path:
    """Write local Metabase dashboard setup notes into the BI output folder."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "metabase_dashboard_notes.md"
    content = """# Metabase Dashboard Notes

This file is generated by the optional v0.5 BI-ready demo.

The demo uses Metabase only as a local dashboard exploration tool. It is not a
production BI deployment, embedded analytics setup, user-management system, or
custom dashboard frontend.

## Recommended database connection

Use these values when Metabase runs through `docker compose`:

| Field | Value |
|---|---|
| Database type | PostgreSQL |
| Host | postgres |
| Port | 5432 |
| Database name | dq_demo |
| Username | dq_user |
| Password | dq_password |

If you connect from a tool running on your host machine instead of from the
Metabase container, use `localhost` as the host.

## Recommended dashboard cards

- Revenue by country
- Orders by month
- Monthly revenue trend
- Orders by source system
- Average order value by country

## Scope note

Do not commit Metabase local state, Docker volumes, dashboard exports with
sensitive configuration, or real customer data.
"""
    output_path.write_text(content, encoding="utf-8")
    return output_path


def write_bi_summary_report(
    output_path: str | Path,
    *,
    input_path: str | Path,
    database_url: str,
    metrics: dict[str, Any],
    table_row_counts: dict[str, int],
    view_names: list[str],
    output_files: dict[str, str],
    table_previews: dict[str, pd.DataFrame] | None = None,
) -> Path:
    """Write a Markdown summary report for the v0.5 BI-ready demo."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# v0.5 BI-ready Reporting Demo Summary",
        "",
        "This report is generated from synthetic demo data.",
        "It shows a repeatable local workflow from messy generated orders to cleaned reporting tables and lightweight SQL views.",
        "",
        "## Scope",
        "",
        "This is an optional BI-ready demo. It is not a production BI platform, data warehouse implementation, Metabase production deployment, embedded analytics feature, custom frontend, cloud deployment, or AI/LLM feature.",
        "",
        "## Input",
        "",
        f"- Input file: `{input_path}`",
        "- Data source: synthetic generated customer/order-style data",
        "- Real customer data: no",
        "",
        "## PostgreSQL reporting database",
        "",
        f"- Database URL: `{_safe_database_url(database_url)}`",
        "- Database role: local reporting database for demo tables and views",
        "",
        "## Runtime summary",
        "",
        f"- Raw row count: {metrics.get('row_count_raw', 0):,}",
        f"- Cleaned row count: {metrics.get('row_count_cleaned', 0):,}",
        f"- Analytics-ready row count: {metrics.get('row_count_analytics', 0):,}",
        f"- Validation issue count: {metrics.get('validation_issue_count', 0):,}",
        f"- Runtime seconds: {metrics.get('runtime_seconds', 0):.3f}",
        "",
        "## Reporting tables created",
        "",
        "| Table | Row count |",
        "|---|---:|",
    ]

    for table_name in REPORTING_TABLE_NAMES:
        lines.append(f"| `{table_name}` | {table_row_counts.get(table_name, 0):,} |")

    lines.extend(
        [
            "",
            "## Reporting views created",
            "",
        ]
    )
    for view_name in view_names:
        lines.append(f"- `{view_name}`")

    lines.extend(
        [
            "",
            "## Output files",
            "",
            "| Output | Path | Size bytes |",
            "|---|---|---:|",
        ]
    )
    for name, path in output_files.items():
        lines.append(f"| {name} | `{path}` | {_safe_file_size(path):,} |")

    if table_previews:
        lines.extend(["", "## Preview tables", ""])
        for table_name, df in table_previews.items():
            if df.empty:
                continue
            lines.extend([f"### `{table_name}`", "", _dataframe_to_markdown(df), ""])

    lines.extend(
        [
            "## Recommended dashboard cards",
            "",
            "- Revenue by country",
            "- Orders by month",
            "- Monthly revenue trend",
            "- Orders by source system",
            "- Average order value by country",
            "",
            "## Local artifact policy",
            "",
            "Do not commit `data/generated/`, `data/output/analytics/`, `data/output/bi/`, PostgreSQL volumes, Metabase local state, or real customer data.",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def validate_bi_outputs(
    *,
    output_files: dict[str, str],
    table_row_counts: dict[str, int],
    view_names: list[str],
) -> None:
    """Validate that expected BI demo outputs were produced."""
    required_files = {"reporting_queries_sql", "bi_summary_report_md", "metabase_dashboard_notes_md"}
    missing_files = sorted(required_files - set(output_files))
    if missing_files:
        raise ValueError(f"Missing expected BI output files: {missing_files}")

    missing_paths = [
        path for path in output_files.values() if not Path(path).exists()
    ]
    if missing_paths:
        raise ValueError(f"BI output paths do not exist: {missing_paths}")

    missing_tables = sorted(set(REPORTING_TABLE_NAMES) - set(table_row_counts))
    if missing_tables:
        raise ValueError(f"Missing expected reporting table counts: {missing_tables}")

    missing_views = sorted(set(REPORTING_VIEW_NAMES) - set(view_names))
    if missing_views:
        raise ValueError(f"Missing expected reporting views: {missing_views}")
