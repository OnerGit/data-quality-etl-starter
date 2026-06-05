from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

InputType = Literal["csv", "excel", "json", "mock-api"]
DbTarget = Literal["none", "sqlite", "postgres"]
Severity = Literal["error", "warning"]
ColumnType = Literal["string", "number", "date", "email"]


class ColumnRule(BaseModel):
    """A portable rule for a column in a messy business dataset."""

    name: str
    dtype: ColumnType = "string"
    required: bool = False
    allow_missing: bool = True
    description: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_rule_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Column rule name cannot be empty")
        return value


class DatasetSchema(BaseModel):
    """Expected dataset contract loaded from a JSON schema file."""

    dataset_name: str
    expected_columns: list[str] = Field(default_factory=list)
    column_rules: list[ColumnRule] = Field(default_factory=list)

    @field_validator("expected_columns")
    @classmethod
    def normalize_expected_columns(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]

    @property
    def rules_by_name(self) -> dict[str, ColumnRule]:
        return {rule.name: rule for rule in self.column_rules}


class WorkflowConfig(BaseModel):
    """Runtime contract for one CLI or API workflow run."""

    input_path: Path
    input_type: InputType
    schema_path: Path
    output_dir: Path
    db_target: DbTarget = "sqlite"
    table_name: str = "cleaned_data"
    database_url: str | None = None
    records_path: str | None = None

    @field_validator("table_name")
    @classmethod
    def validate_table_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("table_name cannot be empty")
        if not value.replace("_", "").isalnum():
            raise ValueError("table_name may contain only letters, numbers, and underscores")
        return value


class ValidationIssue(BaseModel):
    """A structured validation issue that can be rendered to Markdown or JSON."""

    severity: Severity
    code: str
    message: str
    column: str | None = None
    row_number: int | None = None
    value: str | None = None


class QualityReport(BaseModel):
    """Summary of one data quality workflow run."""

    dataset_name: str
    input_path: str
    input_type: InputType
    table_name: str
    row_count_raw: int
    row_count_cleaned: int
    column_count: int
    column_names: list[str]
    expected_columns: list[str]
    missing_expected_columns: list[str]
    unexpected_columns: list[str]
    missing_values_by_column: dict[str, int]
    missing_value_ratio_by_column: dict[str, float]
    duplicate_row_count: int
    duplicate_row_ratio: float
    issues: list[ValidationIssue] = Field(default_factory=list)
    output_files: dict[str, str] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Small response contract for the FastAPI health endpoint."""

    status: str
    service: str
    version: str


class ApiErrorResponse(BaseModel):
    """Optional documented error response shape for the FastAPI service."""

    detail: str
