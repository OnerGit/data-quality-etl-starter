import sqlite3

import pandas as pd

from dq_etl_starter.exporters import export_cleaned_csv, export_to_sqlite


def test_export_cleaned_csv(tmp_path):
    df = pd.DataFrame({"a": [1, 2]})
    output_path = export_cleaned_csv(df, tmp_path / "cleaned.csv")
    assert output_path.exists()


def test_export_to_sqlite(tmp_path):
    df = pd.DataFrame({"a": [1, 2]})
    sqlite_path = export_to_sqlite(df, tmp_path / "out.sqlite", "cleaned")
    assert sqlite_path.exists()
    with sqlite3.connect(sqlite_path) as connection:
        rows = connection.execute("SELECT COUNT(*) FROM cleaned").fetchone()[0]
    assert rows == 2
