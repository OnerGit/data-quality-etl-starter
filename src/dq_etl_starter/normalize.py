from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

import pandas as pd


def normalize_column_name(name: str) -> str:
    """Convert messy spreadsheet-style column names into stable snake_case."""
    normalized = name.strip().lower()
    normalized = re.sub(r"[\s\-\/]+", "_", normalized)
    normalized = re.sub(r"[^a-z0-9_]+", "", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    aliases = {"e_mail": "email", "e_mail_address": "email_address"}
    normalized = aliases.get(normalized, normalized)
    return normalized or "unnamed_column"


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result.columns = [normalize_column_name(str(column)) for column in result.columns]
    return result


def flatten_json_records(records: Iterable[dict[str, Any]], sep: str = "_") -> pd.DataFrame:
    """Flatten nested JSON records into a tabular DataFrame."""
    df = pd.json_normalize(list(records), sep=sep)
    return normalize_column_names(df)


def standardize_text_values(df: pd.DataFrame) -> pd.DataFrame:
    """Trim object/string columns and convert empty strings to missing values."""
    result = df.copy()
    for column in result.select_dtypes(include=["object", "string"]).columns:
        result[column] = result[column].map(lambda value: value.strip() if isinstance(value, str) else value)
        result[column] = result[column].replace("", pd.NA)
    return result
