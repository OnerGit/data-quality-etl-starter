from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_integer_dtype,
    is_numeric_dtype,
    is_string_dtype,
)

DEFAULT_AI_READY_VERSION = "0.6.0"
DEFAULT_OUTPUT_FILES = {
    "schema_profile": "schema_profile.json",
    "data_dictionary": "data_dictionary.json",
    "validation_summary": "validation_summary.json",
    "feature_ready_dataset": "feature_ready_orders.csv",
    "embedding_ready_text_fields": "embedding_ready_text_fields.csv",
    "ai_ready_summary_report": "ai_ready_summary_report.md",
}

_IDENTIFIER_NAMES = {
    "id",
    "order_id",
    "customer_id",
    "user_id",
    "account_id",
    "transaction_id",
}
_CONTACT_NAMES = {
    "email",
    "phone",
    "phone_number",
    "address",
    "street_address",
}
_DATETIME_HINTS = ("date", "time", "timestamp", "created_at", "updated_at")
_NUMERIC_HINTS = (
    "amount",
    "count",
    "price",
    "quantity",
    "rate",
    "revenue",
    "total",
    "value",
)
_TEXT_EXCLUDE_NAMES = _IDENTIFIER_NAMES | _CONTACT_NAMES
_DEFAULT_EMBEDDING_TEXT_COLUMNS = (
    "country",
    "product_category",
    "source_system",
    "customer_segment",
    "order_status",
    "product_name",
    "description",
    "notes",
)


def _json_safe_value(value: Any) -> Any:
    """Convert pandas/numpy values into JSON-friendly scalar values."""
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def _json_safe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {key: _json_safe_value(value) for key, value in record.items()}
        for record in records
    ]


def _infer_profile_dtype(series: pd.Series) -> str:
    if is_bool_dtype(series):
        return "boolean"
    if is_integer_dtype(series):
        return "integer"
    if is_numeric_dtype(series):
        return "number"
    if is_datetime64_any_dtype(series):
        return "datetime"
    return "string"


def _recommended_role(column_name: str, dtype: str) -> str:
    name = column_name.lower()
    if name in _IDENTIFIER_NAMES or name.endswith("_id"):
        return "identifier"
    if name in _CONTACT_NAMES:
        return "contact_field"
    if name in {"source", "source_system", "data_source"}:
        return "lineage_field"
    if any(hint in name for hint in _DATETIME_HINTS) or dtype == "datetime":
        return "datetime_feature"
    if dtype in {"integer", "number"} or any(hint in name for hint in _NUMERIC_HINTS):
        return "numeric_feature"
    if dtype == "boolean":
        return "boolean_feature"
    return "categorical_or_text_feature"


def _example_values(series: pd.Series, limit: int) -> list[Any]:
    values = series.dropna().drop_duplicates().head(limit).tolist()
    return [_json_safe_value(value) for value in values]


def _known_column_description(column_name: str) -> str:
    descriptions = {
        "order_id": "Unique order identifier.",
        "customer_id": "Customer identifier associated with the order.",
        "order_date": "Order date prepared for downstream reporting or analysis.",
        "country": "Country value associated with the order or customer.",
        "product_category": "Product category label used for grouping and reporting.",
        "quantity": "Number of units included in the order.",
        "unit_price": "Unit price for the ordered item.",
        "discount_rate": "Discount rate represented as a decimal fraction.",
        "revenue": "Calculated revenue value after quantity, unit price, and discount rate are applied.",
        "email": "Synthetic contact field used for validation examples.",
        "source_system": "Source system label for lightweight lineage visibility.",
    }
    return descriptions.get(
        column_name,
        f"Column `{column_name}` documented from the cleaned dataset schema profile.",
    )


def _dictionary_notes(column_name: str, role: str) -> str:
    if role == "identifier":
        return "Identifier fields should usually be excluded from numeric model features."
    if role == "contact_field":
        return "Contact fields should be reviewed carefully before any downstream AI or ML use."
    if role == "lineage_field":
        return "Useful for auditability, filtering, and source-system quality checks."
    if role == "datetime_feature":
        return "Can be transformed into time-based features by downstream workflows."
    if column_name == "revenue":
        return "Useful for reporting and feature exploration; check calculation assumptions before reuse."
    return "Review business meaning and downstream suitability before reuse."


def infer_schema_profile(
    df: pd.DataFrame,
    dataset_name: str = "cleaned_orders",
    *,
    example_limit: int = 3,
) -> dict[str, Any]:
    """Infer a lightweight machine-readable schema profile from a cleaned DataFrame."""
    row_count = int(len(df))
    columns: list[dict[str, Any]] = []

    for column_name in df.columns:
        series = df[column_name]
        non_null_count = int(series.notna().sum())
        null_count = int(series.isna().sum())
        unique_count = int(series.nunique(dropna=True))
        dtype = _infer_profile_dtype(series)
        columns.append(
            {
                "name": column_name,
                "dtype": dtype,
                "pandas_dtype": str(series.dtype),
                "non_null_count": non_null_count,
                "null_count": null_count,
                "null_ratio": round(null_count / row_count, 6) if row_count else 0.0,
                "unique_count": unique_count,
                "unique_ratio": round(unique_count / row_count, 6) if row_count else 0.0,
                "example_values": _example_values(series, example_limit),
                "recommended_role": _recommended_role(column_name, dtype),
            }
        )

    return {
        "dataset_name": dataset_name,
        "row_count": row_count,
        "column_count": int(len(df.columns)),
        "columns": columns,
    }


def build_data_dictionary(
    schema_profile: dict[str, Any],
    *,
    description: str | None = None,
) -> dict[str, Any]:
    """Build a data dictionary from a schema profile."""
    dataset_name = str(schema_profile.get("dataset_name", "cleaned_orders"))
    columns = []

    for column in schema_profile.get("columns", []):
        column_name = str(column.get("name"))
        role = str(column.get("recommended_role", "unknown"))
        columns.append(
            {
                "name": column_name,
                "description": _known_column_description(column_name),
                "type": column.get("dtype", "unknown"),
                "role": role,
                "nullable": bool(column.get("null_count", 0) > 0),
                "example_values": column.get("example_values", []),
                "notes": _dictionary_notes(column_name, role),
            }
        )

    return {
        "dataset_name": dataset_name,
        "description": description
        or "Cleaned synthetic customer order data prepared by the data quality workflow.",
        "columns": columns,
    }


def build_validation_summary(
    *,
    dataset_name: str = "cleaned_orders",
    source_file: str | Path | None = None,
    schema_file: str | Path | None = None,
    row_count_before_cleaning: int,
    row_count_after_cleaning: int,
    duplicate_rows_removed: int = 0,
    missing_values_by_column: dict[str, int] | None = None,
    validation_issue_count: int = 0,
    validation_issue_codes: list[str] | None = None,
    quality_report_file: str = "quality_report.json",
) -> dict[str, Any]:
    """Build a compact validation summary for downstream handoff."""
    missing_values_by_column = missing_values_by_column or {}
    columns_with_missing_values = [
        column for column, count in missing_values_by_column.items() if int(count) > 0
    ]

    return {
        "dataset_name": dataset_name,
        "source_file": str(source_file) if source_file is not None else None,
        "schema_file": str(schema_file) if schema_file is not None else None,
        "row_count_before_cleaning": int(row_count_before_cleaning),
        "row_count_after_cleaning": int(row_count_after_cleaning),
        "rows_removed_during_preparation": int(
            max(row_count_before_cleaning - row_count_after_cleaning, 0)
        ),
        "duplicate_rows_removed": int(duplicate_rows_removed),
        "columns_with_missing_values": columns_with_missing_values,
        "validation_issue_count": int(validation_issue_count),
        "validation_issue_codes": sorted(set(validation_issue_codes or [])),
        "quality_report_file": quality_report_file,
        "ai_readiness_notes": [
            "Dataset has been cleaned and documented.",
            "No LLM API was called.",
            "No embeddings were generated.",
            "No model was trained.",
            "Text fields are extracted for later optional embedding workflows.",
        ],
    }


def build_feature_ready_dataset(
    df: pd.DataFrame,
    *,
    drop_identifier_columns: bool = True,
    drop_contact_columns: bool = True,
) -> pd.DataFrame:
    """Build a simple feature-ready tabular dataset without training a model."""
    result = df.copy()
    columns_to_drop: list[str] = []

    for column_name in result.columns:
        name = column_name.lower()
        if drop_identifier_columns and (name in _IDENTIFIER_NAMES or name.endswith("_id")):
            columns_to_drop.append(column_name)
        elif drop_contact_columns and name in _CONTACT_NAMES:
            columns_to_drop.append(column_name)

    result = result.drop(columns=columns_to_drop, errors="ignore")

    if "order_date" in result.columns:
        order_dates = pd.to_datetime(result["order_date"], errors="coerce")
        result["order_year"] = order_dates.dt.year
        result["order_month"] = order_dates.dt.to_period("M").astype(str)
        result = result.drop(columns=["order_date"])

    return result.reset_index(drop=True)


def extract_embedding_ready_text_fields(
    df: pd.DataFrame,
    *,
    record_id_column: str | None = None,
    text_columns: list[str] | None = None,
    exclude_columns: set[str] | None = None,
) -> pd.DataFrame:
    """Extract text-like fields for later optional embedding workflows.

    This function does not call an embedding API and does not create vectors.
    It only prepares a compact text extract that can be reviewed and reused
    by downstream workflows outside this project.
    """
    exclude_columns = set(exclude_columns or _TEXT_EXCLUDE_NAMES)

    if record_id_column is None:
        record_id_column = "order_id" if "order_id" in df.columns else None

    if text_columns is None:
        preferred_columns = [
            column
            for column in _DEFAULT_EMBEDDING_TEXT_COLUMNS
            if column in df.columns
            and column.lower() not in exclude_columns
            and column != record_id_column
        ]

        if preferred_columns:
            text_columns = preferred_columns
        else:
            text_columns = [
                column
                for column in df.columns
                if column.lower() not in exclude_columns
                and column != record_id_column
                and is_string_dtype(df[column])
            ]

    rows: list[dict[str, Any]] = []
    for index, row in df.iterrows():
        record_id = row[record_id_column] if record_id_column else index
        fragments = []

        for column in text_columns:
            value = row.get(column)
            if pd.isna(value) or str(value).strip() == "":
                continue
            fragments.append(f"{column}: {str(value).strip()}")

        rows.append(
            {
                "record_id": _json_safe_value(record_id),
                "text": "; ".join(fragments),
                "source_columns": ",".join(text_columns),
            }
        )

    return pd.DataFrame(rows, columns=["record_id", "text", "source_columns"])

def build_ai_ready_manifest(
    *,
    version: str = DEFAULT_AI_READY_VERSION,
    workflow: str = "ai_ready_data_preparation",
    outputs: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a manifest that explicitly documents scope and output files."""
    return {
        "version": version,
        "workflow": workflow,
        "llm_api_called": False,
        "embedding_generated": False,
        "model_trained": False,
        "outputs": outputs or DEFAULT_OUTPUT_FILES,
        "intended_downstream_use": [
            "BI handoff",
            "ML feature exploration",
            "LLM/RAG preparation outside this project",
            "data quality review",
        ],
        "out_of_scope": [
            "LLM API calls",
            "embeddings generation",
            "model training",
            "RAG chatbot",
            "AI agent",
            "vector database",
        ],
    }


def write_json(data: dict[str, Any], output_path: str | Path) -> Path:
    """Write a dictionary as stable, human-readable JSON."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    return path


def write_ai_ready_summary_report(
    output_path: str | Path,
    *,
    dataset_name: str,
    row_count: int,
    output_files: dict[str, str],
    manifest: dict[str, Any],
) -> Path:
    """Write a Markdown summary for the AI-ready preparation demo."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# AI-ready Data Preparation Summary",
        "",
        f"Dataset name: `{dataset_name}`",
        f"Prepared row count: `{row_count}`",
        "",
        "## Generated outputs",
        "",
    ]

    for label, output_file in output_files.items():
        lines.append(f"- `{label}`: `{output_file}`")

    lines.extend(
        [
            "",
            "## Scope note",
            "",
            "- No LLM API was called.",
            "- No embeddings were generated.",
            "- No model was trained.",
            "- This demo prepares documented, machine-readable data for later BI, ML, or AI workflows.",
            "",
            "## Recommended downstream use",
            "",
        ]
    )

    for item in manifest.get("intended_downstream_use", []):
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Out of scope",
            "",
        ]
    )

    for item in manifest.get("out_of_scope", []):
        lines.append(f"- {item}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def validate_ai_ready_outputs(
    output_dir: str | Path,
    *,
    required_files: list[str] | None = None,
) -> tuple[bool, list[str]]:
    """Check whether expected AI-ready output files exist and are non-empty."""
    output_path = Path(output_dir)
    required_files = required_files or [
        "schema_profile.json",
        "data_dictionary.json",
        "validation_summary.json",
        "feature_ready_orders.csv",
        "embedding_ready_text_fields.csv",
        "ai_ready_manifest.json",
        "ai_ready_summary_report.md",
    ]

    missing_or_empty = []
    for filename in required_files:
        file_path = output_path / filename
        if not file_path.exists() or file_path.stat().st_size == 0:
            missing_or_empty.append(filename)

    return not missing_or_empty, missing_or_empty
