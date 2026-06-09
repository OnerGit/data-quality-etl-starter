from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import Any

import pandas as pd


def _safe_file_size(path: str | Path) -> int:
    file_path = Path(path)
    return file_path.stat().st_size if file_path.exists() and file_path.is_file() else 0


def _to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def prepare_orders_for_analytics(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare cleaned order rows for summary-table and Parquet export.

    The main workflow already normalizes column names, validates schema rules,
    and drops duplicate rows. This function performs a small analytics-specific
    pass: numeric/date coercion, invalid analytics row filtering, revenue
    recalculation, and stable output column ordering.
    """

    required_columns = {
        "order_id",
        "customer_id",
        "order_date",
        "country",
        "product_category",
        "quantity",
        "unit_price",
        "discount_rate",
        "revenue",
        "email",
        "source_system",
    }
    missing = sorted(required_columns - set(df.columns))
    if missing:
        raise ValueError(f"Orders data is missing required analytics columns: {missing}")

    result = df.copy()
    result["country"] = result["country"].fillna("Unknown").replace("", "Unknown")
    result["product_category"] = result["product_category"].fillna("Unknown").replace("", "Unknown")
    result["source_system"] = result["source_system"].fillna("unknown").replace("", "unknown")

    result["quantity"] = _to_numeric(result["quantity"])
    result["unit_price"] = _to_numeric(result["unit_price"])
    result["discount_rate"] = _to_numeric(result["discount_rate"]).fillna(0.0)
    result["revenue"] = _to_numeric(result["revenue"])
    result["order_date"] = pd.to_datetime(result["order_date"], errors="coerce", format="mixed")

    result = result.drop_duplicates(subset=["order_id"], keep="first")
    result = result[
        result["order_id"].notna()
        & result["customer_id"].notna()
        & result["order_date"].notna()
        & result["quantity"].notna()
        & result["unit_price"].notna()
        & (result["quantity"] > 0)
        & (result["unit_price"] > 0)
        & (result["discount_rate"] >= 0)
        & (result["discount_rate"] < 1)
    ].copy()

    result["revenue"] = (result["quantity"] * result["unit_price"] * (1 - result["discount_rate"])).round(2)
    result["order_date"] = result["order_date"].dt.date.astype(str)

    ordered_columns = [
        "order_id",
        "customer_id",
        "order_date",
        "country",
        "product_category",
        "quantity",
        "unit_price",
        "discount_rate",
        "revenue",
        "email",
        "source_system",
    ]
    return result[ordered_columns].reset_index(drop=True)


def build_customer_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Build one row per customer with lightweight order and revenue metrics."""

    summary = (
        df.groupby("customer_id", dropna=False)
        .agg(
            order_count=("order_id", "count"),
            total_revenue=("revenue", "sum"),
            average_order_value=("revenue", "mean"),
            first_order_date=("order_date", "min"),
            last_order_date=("order_date", "max"),
            country=("country", "first"),
            email=("email", "first"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )
    summary["total_revenue"] = summary["total_revenue"].round(2)
    summary["average_order_value"] = summary["average_order_value"].round(2)
    return summary


def build_revenue_by_country(df: pd.DataFrame) -> pd.DataFrame:
    """Build a country-level revenue summary table."""

    summary = (
        df.groupby("country", dropna=False)
        .agg(
            order_count=("order_id", "count"),
            customer_count=("customer_id", "nunique"),
            total_revenue=("revenue", "sum"),
            average_order_value=("revenue", "mean"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )
    summary["total_revenue"] = summary["total_revenue"].round(2)
    summary["average_order_value"] = summary["average_order_value"].round(2)
    return summary


def build_orders_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Build a monthly order and revenue summary table."""

    result = df.copy()
    result["order_month"] = pd.to_datetime(result["order_date"], errors="coerce").dt.to_period("M").astype(str)
    summary = (
        result.groupby("order_month", dropna=False)
        .agg(
            order_count=("order_id", "count"),
            customer_count=("customer_id", "nunique"),
            total_revenue=("revenue", "sum"),
        )
        .reset_index()
        .sort_values("order_month")
    )
    summary["total_revenue"] = summary["total_revenue"].round(2)
    return summary


def build_source_system_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Build a source-system summary for lightweight data lineage visibility."""

    summary = (
        df.groupby("source_system", dropna=False)
        .agg(
            order_count=("order_id", "count"),
            total_revenue=("revenue", "sum"),
        )
        .reset_index()
        .sort_values("order_count", ascending=False)
    )
    summary["total_revenue"] = summary["total_revenue"].round(2)
    return summary


def write_summary_tables(df: pd.DataFrame, output_dir: str | Path) -> dict[str, str]:
    """Write lightweight analytics summary tables as CSV files."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "customer_summary": output_dir / "customer_summary.csv",
        "revenue_by_country": output_dir / "revenue_by_country.csv",
        "orders_by_month": output_dir / "orders_by_month.csv",
        "source_system_summary": output_dir / "source_system_summary.csv",
    }

    build_customer_summary(df).to_csv(outputs["customer_summary"], index=False)
    build_revenue_by_country(df).to_csv(outputs["revenue_by_country"], index=False)
    build_orders_by_month(df).to_csv(outputs["orders_by_month"], index=False)
    build_source_system_summary(df).to_csv(outputs["source_system_summary"], index=False)

    return {name: str(path) for name, path in outputs.items()}


def build_analytics_queries(parquet_path: str | Path) -> str:
    """Return reusable DuckDB SQL examples for querying the Parquet output."""

    parquet_uri = str(Path(parquet_path)).replace("\\", "/").replace("'", "''")
    return f"""-- v0.4 analytics-ready DuckDB query examples
-- These queries read the local Parquet output directly. No data warehouse is required.

SELECT country, ROUND(SUM(revenue), 2) AS total_revenue, COUNT(*) AS order_count
FROM read_parquet('{parquet_uri}')
GROUP BY country
ORDER BY total_revenue DESC
LIMIT 10;

SELECT substr(order_date, 1, 7) AS order_month,
       COUNT(*) AS order_count,
       ROUND(SUM(revenue), 2) AS total_revenue
FROM read_parquet('{parquet_uri}')
GROUP BY order_month
ORDER BY order_month;

SELECT source_system,
       COUNT(*) AS order_count,
       ROUND(SUM(revenue), 2) AS total_revenue
FROM read_parquet('{parquet_uri}')
GROUP BY source_system
ORDER BY order_count DESC;
"""


def write_analytics_queries(output_dir: str | Path, parquet_path: str | Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    query_path = output_dir / "analytics_queries.sql"
    query_path.write_text(build_analytics_queries(parquet_path), encoding="utf-8")
    return query_path


def run_duckdb_queries(parquet_path: str | Path, *, limit: int = 10) -> pd.DataFrame:
    """Run a small DuckDB query against the Parquet output and return a preview."""

    import duckdb

    parquet_uri = str(Path(parquet_path)).replace("\\", "/").replace("'", "''")
    query = f"""
        SELECT
            country,
            ROUND(SUM(revenue), 2) AS total_revenue,
            COUNT(*) AS order_count
        FROM read_parquet('{parquet_uri}')
        GROUP BY country
        ORDER BY total_revenue DESC
        LIMIT {int(limit)}
    """
    return duckdb.sql(query).df()


def _dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Render a small DataFrame as Markdown without requiring tabulate."""

    if df.empty:
        return ""
    columns = [str(column) for column in df.columns]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _index, row in df.iterrows():
        values = [str(row[column]) for column in df.columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_benchmark_report(
    output_path: str | Path,
    *,
    input_path: str | Path,
    metrics: dict[str, Any],
    output_files: dict[str, str],
    duckdb_preview: pd.DataFrame | None = None,
) -> Path:
    """Write a lightweight benchmark report for the analytics demo."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# v0.4 Analytics-ready Export Benchmark Report",
        "",
        "This report is generated from synthetic demo data. It is intended to show a repeatable local workflow from messy input to analytics-ready output.",
        "",
        "## Input",
        "",
        f"- Input file: `{input_path}`",
        "- Data source: synthetic generated customer/order-style data",
        "- Real customer data: no",
        "",
        "## Runtime summary",
        "",
        f"- Raw row count: {metrics.get('row_count_raw', 0):,}",
        f"- Cleaned row count: {metrics.get('row_count_cleaned', 0):,}",
        f"- Analytics-ready row count: {metrics.get('row_count_analytics', 0):,}",
        f"- Validation issue count: {metrics.get('validation_issue_count', 0):,}",
        f"- Runtime seconds: {metrics.get('runtime_seconds', 0):.3f}",
        "",
        "## Output files",
        "",
        "| Output | Path | Size bytes |",
        "|---|---|---:|",
    ]

    for name, path in output_files.items():
        lines.append(f"| {name} | `{path}` | {_safe_file_size(path):,} |")

    if duckdb_preview is not None and not duckdb_preview.empty:
        lines.extend(
            [
                "",
                "## DuckDB query preview",
                "",
                _dataframe_to_markdown(duckdb_preview),
            ]
        )

    lines.extend(
        [
            "",
            "## Scope note",
            "",
            "This is an analytics-ready export demo, not a BI platform, data warehouse, Airflow/dbt/Spark pipeline, cloud deployment, or AI/LLM feature.",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def measure_runtime_seconds(start_time: float) -> float:
    return perf_counter() - start_time
