from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any


def get_database_url(database_url: str | None = None) -> str | None:
    return database_url or os.getenv("DATABASE_URL")


def create_db_connection(db_target: str, sqlite_path: str | Path | None = None, database_url: str | None = None) -> Any:
    """Create a DB connection/engine for pandas DataFrame.to_sql.

    SQLite uses the Python standard library so v0.1 can run without a server.
    PostgreSQL uses SQLAlchemy and an external DATABASE_URL as an optional v0.2 path.
    """
    if db_target == "sqlite":
        if sqlite_path is None:
            raise ValueError("sqlite_path is required for sqlite export")
        Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(sqlite_path)

    if db_target == "postgres":
        url = get_database_url(database_url)
        if not url:
            raise ValueError("DATABASE_URL is required for PostgreSQL export")
        try:
            from sqlalchemy import create_engine
        except ImportError as exc:
            raise RuntimeError("SQLAlchemy is required for PostgreSQL export. Install project dependencies first.") from exc
        return create_engine(url)

    raise ValueError(f"Unsupported db_target: {db_target}")
