from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from dq_etl_starter.normalize import flatten_json_records, normalize_column_names


def read_csv_file(path: str | Path) -> pd.DataFrame:
    return normalize_column_names(pd.read_csv(path))


def read_excel_file(path: str | Path, sheet_name: str | int = 0) -> pd.DataFrame:
    return normalize_column_names(pd.read_excel(path, sheet_name=sheet_name))


def _extract_path(payload: Any, records_path: str | None) -> Any:
    if not records_path:
        return payload

    current = payload
    for part in records_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise KeyError(f"Cannot find records_path segment '{part}' in JSON payload")
    return current


def read_json_file(path: str | Path, records_path: str | None = None) -> pd.DataFrame:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    records = _extract_path(payload, records_path)

    if isinstance(records, dict):
        records = [records]
    if not isinstance(records, list):
        raise TypeError("JSON input must resolve to a list of records or a single object")
    if not all(isinstance(item, dict) for item in records):
        raise TypeError("JSON records must be objects")

    return flatten_json_records(records)
