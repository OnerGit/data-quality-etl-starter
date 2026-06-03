from __future__ import annotations

import re

import pandas as pd

from dq_etl_starter.models import ColumnRule, DatasetSchema, ValidationIssue

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def check_expected_columns(df: pd.DataFrame, schema: DatasetSchema) -> tuple[list[str], list[str], list[ValidationIssue]]:
    actual_columns = set(df.columns)
    expected_columns = set(schema.expected_columns)
    missing = sorted(expected_columns - actual_columns)
    unexpected = sorted(actual_columns - expected_columns) if expected_columns else []

    issues = [
        ValidationIssue(
            severity="error",
            code="MISSING_EXPECTED_COLUMN",
            column=column,
            message=f"Expected column '{column}' is missing from the input dataset.",
        )
        for column in missing
    ]
    issues.extend(
        ValidationIssue(
            severity="warning",
            code="UNEXPECTED_COLUMN",
            column=column,
            message=f"Column '{column}' was found but is not listed in the expected schema.",
        )
        for column in unexpected
    )
    return missing, unexpected, issues


def find_missing_values(df: pd.DataFrame) -> tuple[dict[str, int], dict[str, float]]:
    row_count = len(df)
    counts = df.isna().sum().astype(int).to_dict()
    ratios = {column: (count / row_count if row_count else 0.0) for column, count in counts.items()}
    return counts, ratios


def find_duplicates(df: pd.DataFrame) -> tuple[int, float]:
    row_count = len(df)
    duplicate_count = int(df.duplicated().sum())
    ratio = duplicate_count / row_count if row_count else 0.0
    return duplicate_count, ratio


def _issue_for_bad_value(rule: ColumnRule, row_number: int, value: object, code: str, message: str) -> ValidationIssue:
    return ValidationIssue(
        severity="warning",
        code=code,
        column=rule.name,
        row_number=row_number,
        value=str(value),
        message=message,
    )


def validate_column_rule(df: pd.DataFrame, rule: ColumnRule) -> list[ValidationIssue]:
    if rule.name not in df.columns:
        if rule.required:
            return [
                ValidationIssue(
                    severity="error",
                    code="REQUIRED_COLUMN_NOT_FOUND",
                    column=rule.name,
                    message=f"Required column '{rule.name}' is missing.",
                )
            ]
        return []

    series = df[rule.name]
    issues: list[ValidationIssue] = []

    if not rule.allow_missing:
        missing_rows = series[series.isna()].index.tolist()
        for index in missing_rows:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="MISSING_REQUIRED_VALUE",
                    column=rule.name,
                    row_number=int(index) + 2,
                    message=f"Column '{rule.name}' has a missing required value.",
                )
            )

    non_missing = series.dropna()
    if rule.dtype == "number":
        converted = pd.to_numeric(non_missing, errors="coerce")
        bad_values = non_missing[converted.isna()]
        for index, value in bad_values.items():
            issues.append(_issue_for_bad_value(rule, int(index) + 2, value, "INVALID_NUMBER", f"Value '{value}' cannot be parsed as a number."))
    elif rule.dtype == "date":
        converted = pd.to_datetime(non_missing, errors="coerce", format="mixed")
        bad_values = non_missing[converted.isna()]
        for index, value in bad_values.items():
            issues.append(_issue_for_bad_value(rule, int(index) + 2, value, "INVALID_DATE", f"Value '{value}' cannot be parsed as a date."))
    elif rule.dtype == "email":
        bad_values = non_missing[~non_missing.astype(str).str.match(EMAIL_RE)]
        for index, value in bad_values.items():
            issues.append(_issue_for_bad_value(rule, int(index) + 2, value, "INVALID_EMAIL", f"Value '{value}' is not a valid email format."))

    return issues


def validate_schema(df: pd.DataFrame, schema: DatasetSchema) -> tuple[list[str], list[str], list[ValidationIssue]]:
    missing, unexpected, issues = check_expected_columns(df, schema)
    for rule in schema.column_rules:
        issues.extend(validate_column_rule(df, rule))
    return missing, unexpected, issues
