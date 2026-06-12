from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from dq_etl_starter.ai_ready import (
    build_ai_ready_manifest,
    build_data_dictionary,
    build_feature_ready_dataset,
    build_validation_summary,
    extract_embedding_ready_text_fields,
    infer_schema_profile,
    validate_ai_ready_outputs,
    write_ai_ready_summary_report,
    write_json,
)
from dq_etl_starter.analytics import prepare_orders_for_analytics
from dq_etl_starter.clean import clean_dataframe
from dq_etl_starter.readers import read_csv_file
from dq_etl_starter.services import load_schema
from dq_etl_starter.validate import validate_schema


def run_ai_ready_demo(
    *,
    input_path: str | Path,
    schema_path: str | Path,
    output_dir: str | Path,
    dataset_name: str = "cleaned_orders",
) -> dict[str, str]:
    """Run the optional v0.6 AI-ready data preparation demo."""
    input_path = Path(input_path)
    schema_path = Path(schema_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    schema = load_schema(schema_path)
    raw_df = read_csv_file(input_path)
    missing_expected, unexpected_columns, issues = validate_schema(raw_df, schema)
    cleaned_df = clean_dataframe(raw_df)
    prepared_df = prepare_orders_for_analytics(cleaned_df)

    missing_values_by_column = raw_df.isna().sum().astype(int).to_dict()
    duplicate_rows_removed = int(raw_df.duplicated().sum())
    issue_codes = [issue.code for issue in issues]
    if missing_expected:
        issue_codes.append("MISSING_EXPECTED_COLUMN")
    if unexpected_columns:
        issue_codes.append("UNEXPECTED_COLUMN")

    schema_profile = infer_schema_profile(prepared_df, dataset_name=dataset_name)
    data_dictionary = build_data_dictionary(schema_profile)
    validation_summary = build_validation_summary(
        dataset_name=dataset_name,
        source_file=input_path,
        schema_file=schema_path,
        row_count_before_cleaning=len(raw_df),
        row_count_after_cleaning=len(prepared_df),
        duplicate_rows_removed=duplicate_rows_removed,
        missing_values_by_column=missing_values_by_column,
        validation_issue_count=len(issues),
        validation_issue_codes=issue_codes,
        quality_report_file="quality_report.json",
    )
    feature_ready_df = build_feature_ready_dataset(prepared_df)
    embedding_ready_df = extract_embedding_ready_text_fields(prepared_df)

    output_files = {
        "schema_profile": "schema_profile.json",
        "data_dictionary": "data_dictionary.json",
        "validation_summary": "validation_summary.json",
        "feature_ready_dataset": "feature_ready_orders.csv",
        "embedding_ready_text_fields": "embedding_ready_text_fields.csv",
        "ai_ready_manifest": "ai_ready_manifest.json",
        "ai_ready_summary_report": "ai_ready_summary_report.md",
    }
    manifest = build_ai_ready_manifest(outputs=output_files)

    write_json(schema_profile, output_dir / output_files["schema_profile"])
    write_json(data_dictionary, output_dir / output_files["data_dictionary"])
    write_json(validation_summary, output_dir / output_files["validation_summary"])
    write_json(manifest, output_dir / output_files["ai_ready_manifest"])

    feature_ready_df.to_csv(output_dir / output_files["feature_ready_dataset"], index=False)
    embedding_ready_df.to_csv(
        output_dir / output_files["embedding_ready_text_fields"], index=False
    )
    write_ai_ready_summary_report(
        output_dir / output_files["ai_ready_summary_report"],
        dataset_name=dataset_name,
        row_count=len(prepared_df),
        output_files=output_files,
        manifest=manifest,
    )

    is_valid, missing_files = validate_ai_ready_outputs(output_dir)
    if not is_valid:
        raise RuntimeError(f"Missing or empty AI-ready outputs: {missing_files}")

    return {key: str(output_dir / filename) for key, filename in output_files.items()}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the optional v0.6 AI-ready data preparation demo."
    )
    parser.add_argument("--input", required=True, help="Input generated orders CSV file.")
    parser.add_argument("--schema", required=True, help="Expected schema JSON file.")
    parser.add_argument(
        "--output-dir",
        default="data/output/ai_ready",
        help="Directory for AI-ready output files.",
    )
    parser.add_argument(
        "--dataset-name",
        default="cleaned_orders",
        help="Dataset name used in generated metadata files.",
    )
    return parser


def _print_completion_message(
    *,
    input_path: str | Path,
    schema_path: str | Path,
    output_dir: str | Path,
    dataset_name: str,
    outputs: dict[str, str],
) -> None:
    print("v0.6 AI-ready data preparation demo completed")
    print("=" * 56)
    print(f"Input file: {input_path}")
    print(f"Schema file: {schema_path}")
    print(f"Output directory: {output_dir}")
    print(f"Dataset name: {dataset_name}")
    print()
    print("Generated outputs")
    print("-" * 56)
    for label, output_path in outputs.items():
        print(f"- {label}: {output_path}")
    print()
    print("Scope note")
    print("-" * 56)
    print("No LLM API was called.")
    print("No embeddings were generated.")
    print("No model was trained.")
    print(
        "This demo prepares documented, machine-readable data for later BI, ML, or AI workflows."
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    outputs = run_ai_ready_demo(
        input_path=args.input,
        schema_path=args.schema,
        output_dir=args.output_dir,
        dataset_name=args.dataset_name,
    )
    _print_completion_message(
        input_path=args.input,
        schema_path=args.schema,
        output_dir=args.output_dir,
        dataset_name=args.dataset_name,
        outputs=outputs,
    )


if __name__ == "__main__":
    main()
