from __future__ import annotations

import os

import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from dq_etl_starter.exporters import export_to_postgres


pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="DATABASE_URL is not set; skipping PostgreSQL integration test.",
)
def test_export_to_postgres_writes_table() -> None:
    table_name = "test_cleaned_customers"

    df = pd.DataFrame(
        {
            "customer_id": [1, 2],
            "customer_name": ["Alice", "Bob"],
            "email": ["alice@example.com", "bob@example.com"],
        }
    )

    exported_table = export_to_postgres(
        df,
        table_name=table_name,
    )

    assert exported_table == table_name

    engine = create_engine(os.environ["DATABASE_URL"])

    try:
        with engine.connect() as conn:
            row_count = conn.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            ).scalar_one()

        assert row_count == 2

    finally:
        engine.dispose()