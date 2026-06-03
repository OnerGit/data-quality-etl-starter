from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from dq_etl_starter.normalize import flatten_json_records


def load_mock_api_response(path: str | Path) -> dict[str, Any]:
    """Load a static API-like response without external network calls or API keys."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("Mock API response must be a JSON object")
    return payload


def extract_records_from_response(payload: dict[str, Any], records_path: str = "data.orders") -> list[dict[str, Any]]:
    current: Any = payload
    for part in records_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise KeyError(f"Cannot find records_path segment '{part}' in mock API response")
    if not isinstance(current, list) or not all(isinstance(item, dict) for item in current):
        raise TypeError("Mock API records path must resolve to a list of objects")
    return current


def mock_api_response_to_dataframe(path: str | Path, records_path: str = "data.orders") -> pd.DataFrame:
    payload = load_mock_api_response(path)
    records = extract_records_from_response(payload, records_path=records_path)
    return flatten_json_records(records)
