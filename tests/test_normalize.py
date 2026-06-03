import pandas as pd

from dq_etl_starter.normalize import flatten_json_records, normalize_column_name, normalize_column_names


def test_normalize_column_name():
    assert normalize_column_name(" Full Name ") == "full_name"
    assert normalize_column_name("Customer-ID") == "customer_id"


def test_normalize_column_names():
    df = pd.DataFrame({" Full Name ": ["Alice"], "E-mail": ["a@example.com"]})
    normalized = normalize_column_names(df)
    assert list(normalized.columns) == ["full_name", "email"]


def test_flatten_json_records():
    records = [{"id": 1, "profile": {"email": "a@example.com"}}]
    df = flatten_json_records(records)
    assert "profile_email" in df.columns
