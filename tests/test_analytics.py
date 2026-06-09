from __future__ import annotations

from pathlib import Path

import pandas as pd

from dq_etl_starter.analytics import (
    build_customer_summary,
    build_orders_by_month,
    build_revenue_by_country,
    prepare_orders_for_analytics,
    run_duckdb_queries,
    write_analytics_queries,
    write_benchmark_report,
    write_summary_tables,
)
from dq_etl_starter.exporters import export_to_parquet


def _orders_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["ORD-1", "ORD-2", "ORD-3", "ORD-3", "ORD-4"],
            "customer_id": ["CUST-1", "CUST-1", "CUST-2", "CUST-2", "CUST-3"],
            "order_date": ["2024-01-10", "2024-01-20", "2024-02-05", "2024-02-05", "not-a-date"],
            "country": ["Singapore", "Singapore", "United States", "United States", "Germany"],
            "product_category": ["Software", "Hardware", "Training", "Training", "Consulting"],
            "quantity": [2, 1, 3, 3, 1],
            "unit_price": [10.0, 20.0, 30.0, 30.0, 100.0],
            "discount_rate": [0.0, 0.1, 0.0, 0.0, 0.0],
            "revenue": [20.0, 18.0, 90.0, 90.0, 100.0],
            "email": ["a@example.com", "a@example.com", "b@example.com", "b@example.com", "c@example.com"],
            "source_system": ["shopify", "stripe", "manual_csv", "manual_csv", "legacy_crm"],
        }
    )


def test_prepare_orders_for_analytics_filters_invalid_rows_and_deduplicates() -> None:
    result = prepare_orders_for_analytics(_orders_df())

    assert len(result) == 3
    assert result["order_id"].tolist() == ["ORD-1", "ORD-2", "ORD-3"]
    assert result["revenue"].tolist() == [20.0, 18.0, 90.0]


def test_summary_tables_have_expected_columns() -> None:
    prepared = prepare_orders_for_analytics(_orders_df())

    customer_summary = build_customer_summary(prepared)
    revenue_by_country = build_revenue_by_country(prepared)
    orders_by_month = build_orders_by_month(prepared)

    assert {"customer_id", "order_count", "total_revenue"}.issubset(customer_summary.columns)
    assert {"country", "order_count", "total_revenue"}.issubset(revenue_by_country.columns)
    assert {"order_month", "order_count", "total_revenue"}.issubset(orders_by_month.columns)


def test_write_summary_tables_and_queries(tmp_path: Path) -> None:
    prepared = prepare_orders_for_analytics(_orders_df())
    parquet_path = tmp_path / "cleaned_orders.parquet"
    export_to_parquet(prepared, parquet_path)

    summary_files = write_summary_tables(prepared, tmp_path)
    query_path = write_analytics_queries(tmp_path, parquet_path)

    assert Path(summary_files["customer_summary"]).exists()
    assert Path(summary_files["revenue_by_country"]).exists()
    assert Path(summary_files["orders_by_month"]).exists()
    assert query_path.exists()
    assert "read_parquet" in query_path.read_text(encoding="utf-8")


def test_run_duckdb_queries_returns_preview(tmp_path: Path) -> None:
    prepared = prepare_orders_for_analytics(_orders_df())
    parquet_path = export_to_parquet(prepared, tmp_path / "cleaned_orders.parquet")

    preview = run_duckdb_queries(parquet_path, limit=5)

    assert not preview.empty
    assert {"country", "total_revenue", "order_count"}.issubset(preview.columns)


def test_write_benchmark_report(tmp_path: Path) -> None:
    prepared = prepare_orders_for_analytics(_orders_df())
    cleaned_csv = tmp_path / "cleaned_orders.csv"
    prepared.to_csv(cleaned_csv, index=False)

    report_path = write_benchmark_report(
        tmp_path / "benchmark_report.md",
        input_path="data/generated/orders_1k.csv",
        metrics={
            "row_count_raw": 5,
            "row_count_cleaned": 4,
            "row_count_analytics": len(prepared),
            "validation_issue_count": 2,
            "runtime_seconds": 0.123,
        },
        output_files={"cleaned_orders_csv": str(cleaned_csv)},
        duckdb_preview=build_revenue_by_country(prepared),
    )

    content = report_path.read_text(encoding="utf-8")
    assert report_path.exists()
    assert "Raw row count" in content
    assert "Runtime seconds" in content
    assert "cleaned_orders_csv" in content
