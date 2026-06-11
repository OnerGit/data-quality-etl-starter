from __future__ import annotations

from pathlib import Path

import pandas as pd

from dq_etl_starter.analytics import prepare_orders_for_analytics
from dq_etl_starter.bi import (
    REPORTING_TABLE_NAMES,
    REPORTING_VIEW_NAMES,
    build_reporting_tables,
    validate_bi_outputs,
    write_bi_summary_report,
    write_metabase_dashboard_notes,
    write_reporting_queries,
)


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


def test_build_reporting_tables_from_small_dataframe() -> None:
    prepared = prepare_orders_for_analytics(_orders_df())
    tables = build_reporting_tables(prepared)

    assert set(tables) == set(REPORTING_TABLE_NAMES)
    assert len(tables["cleaned_orders"]) == 3
    assert {"country", "order_count", "total_revenue"}.issubset(
        tables["revenue_by_country"].columns
    )
    assert {"order_month", "order_count", "total_revenue"}.issubset(
        tables["orders_by_month"].columns
    )
    assert {"source_system", "order_count", "total_revenue"}.issubset(
        tables["source_system_summary"].columns
    )


def test_write_reporting_queries_and_metabase_notes(tmp_path: Path) -> None:
    query_path = write_reporting_queries(tmp_path)
    notes_path = write_metabase_dashboard_notes(tmp_path)

    query_content = query_path.read_text(encoding="utf-8")
    notes_content = notes_path.read_text(encoding="utf-8")

    assert query_path.exists()
    assert "CREATE OR REPLACE VIEW vw_revenue_by_country" in query_content
    assert "Recommended dashboard card queries" in query_content
    assert notes_path.exists()
    assert "Host | postgres" in notes_content
    assert "not a\nproduction BI deployment" in notes_content


def test_write_bi_summary_report(tmp_path: Path) -> None:
    prepared = prepare_orders_for_analytics(_orders_df())
    tables = build_reporting_tables(prepared)
    query_path = write_reporting_queries(tmp_path)
    notes_path = write_metabase_dashboard_notes(tmp_path)
    output_files = {
        "reporting_queries_sql": str(query_path),
        "metabase_dashboard_notes_md": str(notes_path),
    }

    report_path = write_bi_summary_report(
        tmp_path / "bi_summary_report.md",
        input_path="data/generated/orders_1k.csv",
        database_url="postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo",
        metrics={
            "row_count_raw": 5,
            "row_count_cleaned": 4,
            "row_count_analytics": len(prepared),
            "validation_issue_count": 2,
            "runtime_seconds": 0.123,
        },
        table_row_counts={name: len(df) for name, df in tables.items()},
        view_names=REPORTING_VIEW_NAMES.copy(),
        output_files=output_files,
        table_previews={"revenue_by_country": tables["revenue_by_country"]},
    )

    content = report_path.read_text(encoding="utf-8")
    assert report_path.exists()
    assert "v0.5 BI-ready Reporting Demo Summary" in content
    assert "dq_user:***@localhost" in content
    assert "Reporting tables created" in content
    assert "vw_monthly_revenue_trend" in content
    assert "Revenue by country" in content


def test_validate_bi_outputs_accepts_expected_files(tmp_path: Path) -> None:
    query_path = write_reporting_queries(tmp_path)
    notes_path = write_metabase_dashboard_notes(tmp_path)
    report_path = tmp_path / "bi_summary_report.md"
    report_path.write_text("# Demo\n", encoding="utf-8")

    validate_bi_outputs(
        output_files={
            "reporting_queries_sql": str(query_path),
            "metabase_dashboard_notes_md": str(notes_path),
            "bi_summary_report_md": str(report_path),
        },
        table_row_counts={name: 1 for name in REPORTING_TABLE_NAMES},
        view_names=REPORTING_VIEW_NAMES.copy(),
    )
