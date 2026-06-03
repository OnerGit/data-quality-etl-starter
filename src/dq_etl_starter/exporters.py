from __future__ import annotations

from pathlib import Path

import pandas as pd

from dq_etl_starter.db import create_db_connection


def export_cleaned_csv(df: pd.DataFrame, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def export_cleaned_excel(df: pd.DataFrame, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)
    return output_path


def export_to_sqlite(df: pd.DataFrame, sqlite_path: str | Path, table_name: str) -> Path:
    sqlite_path = Path(sqlite_path)
    connection = create_db_connection("sqlite", sqlite_path=sqlite_path)
    try:
        df.to_sql(table_name, con=connection, if_exists="replace", index=False)
    finally:
        connection.close()
    return sqlite_path


def export_to_postgres(df: pd.DataFrame, table_name: str, database_url: str | None = None) -> str:
    engine = create_db_connection("postgres", database_url=database_url)
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)
    return table_name
