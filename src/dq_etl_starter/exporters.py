from __future__ import annotations

from pathlib import Path

import pandas as pd

from dq_etl_starter.db import create_db_engine


def export_cleaned_csv(df: pd.DataFrame, output_path: str | Path) -> Path:
    """Export the cleaned DataFrame to CSV."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)

    return output_path


def export_cleaned_excel(df: pd.DataFrame, output_path: str | Path) -> Path:
    """Export the cleaned DataFrame to Excel."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_excel(output_path, index=False)

    return output_path


def export_to_sqlite(
    df: pd.DataFrame,
    sqlite_path: str | Path,
    table_name: str,
    if_exists: str = "replace",
) -> Path:
    """Export the cleaned DataFrame to a local SQLite database."""
    sqlite_path = Path(sqlite_path)

    engine = create_db_engine(
        db_target="sqlite",
        sqlite_path=sqlite_path,
    )

    try:
        df.to_sql(
            table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
        )
    finally:
        engine.dispose()

    return sqlite_path


def export_to_postgres(
    df: pd.DataFrame,
    table_name: str,
    database_url: str | None = None,
    if_exists: str = "replace",
) -> str:
    """Export the cleaned DataFrame to PostgreSQL.

    PostgreSQL is optional. If database_url is not provided, DATABASE_URL is used.
    """

    engine = None

    try:
        engine = create_db_engine(
            db_target="postgres",
            database_url=database_url,
        )

        df.to_sql(
            table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
        )

    except ValueError:
        raise

    except Exception as exc:
        raise RuntimeError(
            "PostgreSQL export failed. Please check that DATABASE_URL is set, "
            "the PostgreSQL container is running, the credentials are correct, "
            "and psycopg is installed."
        ) from exc

    finally:
        if engine is not None:
            engine.dispose()

    return table_name