from __future__ import annotations

import pandas as pd

from dq_etl_starter.ai_ready import (
    build_ai_ready_manifest,
    build_data_dictionary,
    build_feature_ready_dataset,
    build_validation_summary,
    extract_embedding_ready_text_fields,
    infer_schema_profile,
)


def _small_orders_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "order_id": "ORD-000001",
                "customer_id": "CUS-0001",
                "order_date": "2026-01-01",
                "country": "United States",
                "product_category": "Electronics",
                "quantity": 2,
                "unit_price": 100.0,
                "discount_rate": 0.1,
                "revenue": 180.0,
                "email": "alice@example.com",
                "source_system": "web",
            },
            {
                "order_id": "ORD-000002",
                "customer_id": "CUS-0002",
                "order_date": "2026-01-02",
                "country": "Singapore",
                "product_category": "Office",
                "quantity": 1,
                "unit_price": 50.0,
                "discount_rate": 0.0,
                "revenue": 50.0,
                "email": "bob@example.com",
                "source_system": "api",
            },
        ]
    )


def test_infer_schema_profile_from_small_dataframe() -> None:
    profile = infer_schema_profile(_small_orders_df(), dataset_name="cleaned_orders")

    assert profile["dataset_name"] == "cleaned_orders"
    assert profile["row_count"] == 2
    assert profile["column_count"] == 11
    assert profile["columns"][0]["name"] == "order_id"
    assert profile["columns"][0]["recommended_role"] == "identifier"


def test_build_data_dictionary_contains_expected_columns() -> None:
    profile = infer_schema_profile(_small_orders_df(), dataset_name="cleaned_orders")
    dictionary = build_data_dictionary(profile)

    column_names = [column["name"] for column in dictionary["columns"]]
    assert "order_id" in column_names
    assert "revenue" in column_names
    assert dictionary["columns"][0]["role"] == "identifier"


def test_build_validation_summary_contains_quality_notes() -> None:
    summary = build_validation_summary(
        dataset_name="cleaned_orders",
        source_file="data/generated/orders_1k.csv",
        schema_file="data/expected/generated_order_schema.json",
        row_count_before_cleaning=10,
        row_count_after_cleaning=8,
        duplicate_rows_removed=1,
        missing_values_by_column={"email": 2, "country": 0},
        validation_issue_count=2,
        validation_issue_codes=["INVALID_EMAIL"],
    )

    assert summary["rows_removed_during_preparation"] == 2
    assert summary["duplicate_rows_removed"] == 1
    assert summary["columns_with_missing_values"] == ["email"]
    assert "No LLM API was called." in summary["ai_readiness_notes"]


def test_build_feature_ready_dataset_drops_identifier_only_columns_if_configured() -> None:
    feature_ready = build_feature_ready_dataset(_small_orders_df())

    assert "order_id" not in feature_ready.columns
    assert "customer_id" not in feature_ready.columns
    assert "email" not in feature_ready.columns
    assert "order_year" in feature_ready.columns
    assert "order_month" in feature_ready.columns
    assert "revenue" in feature_ready.columns


def test_extract_embedding_ready_text_fields() -> None:
    text_fields = extract_embedding_ready_text_fields(_small_orders_df())

    assert list(text_fields.columns) == ["record_id", "text", "source_columns"]
    assert text_fields.loc[0, "record_id"] == "ORD-000001"
    assert "Electronics" in text_fields.loc[0, "text"]
    assert "alice@example.com" not in text_fields.loc[0, "text"]


def test_build_ai_ready_manifest_marks_no_llm_api_called() -> None:
    manifest = build_ai_ready_manifest()

    assert manifest["version"] == "0.6.0"
    assert manifest["llm_api_called"] is False
    assert manifest["embedding_generated"] is False
    assert manifest["model_trained"] is False
