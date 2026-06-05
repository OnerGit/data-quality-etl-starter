from __future__ import annotations

import json

from fastapi.testclient import TestClient

from dq_etl_starter.api import app

client = TestClient(app)


CUSTOMER_SCHEMA = {
    "dataset_name": "api_customers",
    "expected_columns": ["customer_id", "email", "country"],
    "column_rules": [
        {
            "name": "customer_id",
            "dtype": "number",
            "required": True,
            "allow_missing": False,
        },
        {
            "name": "email",
            "dtype": "email",
            "required": True,
            "allow_missing": False,
        },
    ],
}

CUSTOMER_CSV = """customer_id,email,country\n1,alice@example.com,usa\n2,not-an-email,UK\n2,not-an-email,UK\n3,,Singapore\n"""


def _schema_file_tuple():
    return (
        "customer_schema.json",
        json.dumps(CUSTOMER_SCHEMA),
        "application/json",
    )


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "data-quality-etl-starter-api",
        "version": "0.3.0",
    }


def test_validate_csv_success() -> None:
    response = client.post(
        "/validate",
        data={"input_type": "csv"},
        files={
            "file": ("customers.csv", CUSTOMER_CSV, "text/csv"),
            "schema_file": _schema_file_tuple(),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["dataset_name"] == "api_customers"
    assert payload["input_type"] == "csv"
    assert payload["row_count_raw"] == 4
    assert payload["row_count_cleaned"] == 3
    assert payload["duplicate_row_count"] == 1
    assert "missing_values_by_column" in payload
    assert "email" in payload["missing_values_by_column"]
    assert any(issue["code"] == "INVALID_EMAIL" for issue in payload["issues"])


def test_validate_missing_schema_file() -> None:
    response = client.post(
        "/validate",
        data={"input_type": "csv"},
        files={"file": ("customers.csv", CUSTOMER_CSV, "text/csv")},
    )

    assert response.status_code == 400
    assert "schema_file is required" in response.json()["detail"]


def test_validate_unsupported_input_type() -> None:
    response = client.post(
        "/validate",
        data={"input_type": "xml"},
        files={
            "file": ("customers.xml", "<customers />", "application/xml"),
            "schema_file": _schema_file_tuple(),
        },
    )

    assert response.status_code == 400
    assert "Unsupported input_type" in response.json()["detail"]


def test_validate_response_contains_quality_report_fields() -> None:
    response = client.post(
        "/validate",
        data={"input_type": "csv"},
        files={
            "file": ("customers.csv", CUSTOMER_CSV, "text/csv"),
            "schema_file": _schema_file_tuple(),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    expected_fields = {
        "dataset_name",
        "input_type",
        "row_count_raw",
        "row_count_cleaned",
        "column_count",
        "column_names",
        "expected_columns",
        "missing_expected_columns",
        "unexpected_columns",
        "missing_values_by_column",
        "duplicate_row_count",
        "issues",
        "output_files",
    }
    assert expected_fields.issubset(payload.keys())
