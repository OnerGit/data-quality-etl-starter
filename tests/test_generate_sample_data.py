from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from generate_sample_data import (  # noqa: E402
    NORMALIZED_ORDER_COLUMNS,
    generate_orders_dataframe,
    write_orders_csv,
)
from dq_etl_starter.normalize import normalize_column_names  # noqa: E402


def test_generate_orders_dataframe_row_count_and_columns() -> None:
    df = generate_orders_dataframe(rows=100, seed=42)
    normalized_df = normalize_column_names(df)

    assert len(df) == 100
    assert set(NORMALIZED_ORDER_COLUMNS).issubset(normalized_df.columns)


def test_generate_orders_dataframe_is_deterministic_with_same_seed() -> None:
    first = generate_orders_dataframe(rows=100, seed=42)
    second = generate_orders_dataframe(rows=100, seed=42)

    pd.testing.assert_frame_equal(first, second)


def test_generate_orders_dataframe_changes_with_different_seed() -> None:
    first = generate_orders_dataframe(rows=100, seed=42)
    second = generate_orders_dataframe(rows=100, seed=99)

    assert not first.equals(second)


def test_generate_orders_dataframe_includes_intentional_issues() -> None:
    df = generate_orders_dataframe(rows=200, seed=42)
    normalized_df = normalize_column_names(df)

    assert normalized_df["email"].astype(str).str.contains("invalid-email", regex=False).any()
    assert (pd.to_numeric(normalized_df["quantity"], errors="coerce") < 0).any()
    assert normalized_df.duplicated().sum() > 0


def test_write_orders_csv(tmp_path: Path) -> None:
    output_path = tmp_path / "orders.csv"
    df = generate_orders_dataframe(rows=25, seed=42)

    result = write_orders_csv(df, output_path)
    loaded = pd.read_csv(result)

    assert result == output_path
    assert output_path.exists()
    assert len(loaded) == 25
