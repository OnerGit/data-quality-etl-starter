from __future__ import annotations

from dq_etl_starter.bi import (
    REPORTING_VIEW_NAMES,
    build_dashboard_query_examples,
    build_reporting_queries_sql,
    build_reporting_views_sql,
)


def test_reporting_views_sql_contains_expected_views() -> None:
    sql = build_reporting_views_sql()

    for view_name in REPORTING_VIEW_NAMES:
        assert view_name in sql

    assert "revenue_by_country" in sql
    assert "orders_by_month" in sql
    assert "source_system_summary" in sql
    assert "ROUND((total_revenue::numeric / NULLIF(order_count, 0)), 2)" in sql


def test_dashboard_query_examples_reference_views_not_raw_files() -> None:
    sql = build_dashboard_query_examples()

    assert "FROM vw_revenue_by_country" in sql
    assert "FROM vw_orders_by_month" in sql
    assert "FROM vw_monthly_revenue_trend" in sql
    assert "read_parquet" not in sql


def test_reporting_queries_sql_combines_views_and_dashboard_queries() -> None:
    sql = build_reporting_queries_sql()

    assert "v0.5 BI-ready reporting SQL" in sql
    assert "CREATE OR REPLACE VIEW" in sql
    assert "Recommended dashboard card queries" in sql
    assert "Average order value by country" in sql
