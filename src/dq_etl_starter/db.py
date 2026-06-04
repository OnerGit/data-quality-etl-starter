from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_database_url(database_url: str | None = None) -> str | None:
    """Return an explicit database URL or fall back to the DATABASE_URL env var."""
    return database_url or os.getenv("DATABASE_URL")


def create_db_engine(
    db_target: str,
    sqlite_path: str | Path | None = None,
    database_url: str | None = None,
) -> Engine:
    """Create a SQLAlchemy engine for SQLite or PostgreSQL.

    SQLite remains the default local database target.
    PostgreSQL is an optional v0.2 export target controlled by DATABASE_URL.
    """

    if db_target == "sqlite":
        if sqlite_path is None:
            raise ValueError("sqlite_path is required when db_target='sqlite'.")

        sqlite_path = Path(sqlite_path)
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)

        return create_engine(f"sqlite:///{sqlite_path}")

    if db_target == "postgres":
        url = get_database_url(database_url)

        if not url:
            raise ValueError(
                "DATABASE_URL is required when db_target='postgres'. "
                "Example: postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo"
            )

        return create_engine(url, pool_pre_ping=True)

    raise ValueError(
        f"Unsupported db_target: {db_target}. "
        "Supported values are: sqlite, postgres."
    )


def create_db_connection(
    db_target: str,
    sqlite_path: str | Path | None = None,
    database_url: str | None = None,
) -> Engine:
    """Backward-compatible wrapper for older code that imported create_db_connection."""
    return create_db_engine(
        db_target=db_target,
        sqlite_path=sqlite_path,
        database_url=database_url,
    )