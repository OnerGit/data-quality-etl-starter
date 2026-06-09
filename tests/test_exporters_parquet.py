from __future__ import annotations

from pathlib import Path

import pandas as pd

from dq_etl_starter.exporters import export_to_parquet


def test_export_to_parquet_writes_file_and_preserves_rows(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "order_id": ["ORD-00000001", "ORD-00000002"],
            "country": ["Singapore", "United States"],
            "revenue": [120.5, 88.0],
        }
    )
    output_path = tmp_path / "cleaned_orders.parquet"

    result = export_to_parquet(df, output_path)
    loaded = pd.read_parquet(result)

    assert result == output_path
    assert output_path.exists()
    assert len(loaded) == 2
    assert list(loaded.columns) == ["order_id", "country", "revenue"]
