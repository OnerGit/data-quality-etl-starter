import pandas as pd

from dq_etl_starter.models import ColumnRule, DatasetSchema
from dq_etl_starter.validate import find_duplicates, find_missing_values, validate_schema


def test_find_missing_values():
    df = pd.DataFrame({"a": [1, None], "b": ["x", "y"]})
    counts, ratios = find_missing_values(df)
    assert counts["a"] == 1
    assert ratios["a"] == 0.5


def test_find_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2]})
    count, ratio = find_duplicates(df)
    assert count == 1
    assert round(ratio, 4) == 0.3333


def test_validate_schema_detects_missing_expected_and_bad_email():
    schema = DatasetSchema(
        dataset_name="test",
        expected_columns=["email", "revenue"],
        column_rules=[ColumnRule(name="email", dtype="email", required=True, allow_missing=False)],
    )
    df = pd.DataFrame({"email": ["not-an-email", None]})
    missing, unexpected, issues = validate_schema(df, schema)
    assert "revenue" in missing
    assert any(issue.code == "INVALID_EMAIL" for issue in issues)
    assert any(issue.code == "MISSING_REQUIRED_VALUE" for issue in issues)
