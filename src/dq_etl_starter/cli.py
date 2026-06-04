from __future__ import annotations

import argparse
from pathlib import Path

from dq_etl_starter.clean import clean_dataframe
from dq_etl_starter.exporters import (
    export_cleaned_csv,
    export_to_postgres,
    export_to_sqlite,
)
from dq_etl_starter.mock_api import mock_api_response_to_dataframe
from dq_etl_starter.models import DatasetSchema, WorkflowConfig
from dq_etl_starter.readers import read_csv_file, read_excel_file, read_json_file
from dq_etl_starter.report import (
    build_quality_report,
    export_report_json,
    export_report_markdown,
)
from dq_etl_starter.validate import validate_schema


def load_schema(path: str | Path) -> DatasetSchema:
    """Load the expected dataset schema from a JSON file."""
    return DatasetSchema.model_validate_json(
        Path(path).read_text(encoding="utf-8")
    )


def read_input(config: WorkflowConfig):
    """Read one supported input type into a normalized DataFrame."""
    if config.input_type == "csv":
        return read_csv_file(config.input_path)

    if config.input_type == "excel":
        return read_excel_file(config.input_path)

    if config.input_type == "json":
        return read_json_file(
            config.input_path,
            records_path=config.records_path,
        )

    if config.input_type == "mock-api":
        return mock_api_response_to_dataframe(
            config.input_path,
            records_path=config.records_path or "data.orders",
        )

    raise ValueError(f"Unsupported input type: {config.input_type}")


def run_workflow(config: WorkflowConfig):
    """Run the complete data quality ETL workflow."""
    config.output_dir.mkdir(parents=True, exist_ok=True)

    schema = load_schema(config.schema_path)
    raw_df = read_input(config)

    missing_expected, unexpected, issues = validate_schema(raw_df, schema)

    cleaned_df = clean_dataframe(raw_df)

    cleaned_csv_path = config.output_dir / f"{config.table_name}.csv"
    export_cleaned_csv(cleaned_df, cleaned_csv_path)

    output_files: dict[str, str] = {
        "cleaned_csv": str(cleaned_csv_path),
    }

    if config.db_target == "sqlite":
        sqlite_path = config.output_dir / "etl_output.sqlite"
        export_to_sqlite(
            cleaned_df,
            sqlite_path=sqlite_path,
            table_name=config.table_name,
        )
        output_files["sqlite"] = str(sqlite_path)

    elif config.db_target == "postgres":
        exported_table = export_to_postgres(
            cleaned_df,
            table_name=config.table_name,
            database_url=config.database_url,
        )
        output_files["postgres_table"] = exported_table

    elif config.db_target == "none":
        output_files["database"] = "not exported"

    else:
        raise ValueError(f"Unsupported db_target: {config.db_target}")

    report_md_path = config.output_dir / "quality_report.md"
    report_json_path = config.output_dir / "quality_report.json"

    output_files["quality_report_md"] = str(report_md_path)
    output_files["quality_report_json"] = str(report_json_path)

    report = build_quality_report(
        config=config,
        schema=schema,
        raw_df=raw_df,
        cleaned_df=cleaned_df,
        missing_expected_columns=missing_expected,
        unexpected_columns=unexpected,
        issues=issues,
        output_files=output_files,
    )

    export_report_markdown(report, report_md_path)
    export_report_json(report, report_json_path)

    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a small data quality ETL workflow."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Run the ETL workflow",
    )

    run_parser.add_argument(
        "--input",
        required=True,
        dest="input_path",
    )

    run_parser.add_argument(
        "--input-type",
        required=True,
        choices=["csv", "excel", "json", "mock-api"],
    )

    run_parser.add_argument(
        "--schema",
        required=True,
        dest="schema_path",
    )

    run_parser.add_argument(
        "--output-dir",
        required=True,
    )

    run_parser.add_argument(
        "--db-target",
        default="sqlite",
        choices=["none", "sqlite", "postgres"],
        help="Database export target. SQLite is the default. PostgreSQL is optional.",
    )

    run_parser.add_argument(
        "--table-name",
        default="cleaned_data",
        help="Target table name for SQLite or PostgreSQL export.",
    )

    run_parser.add_argument(
        "--database-url",
        default=None,
        help="Optional PostgreSQL connection URL. If omitted, DATABASE_URL is used.",
    )

    run_parser.add_argument(
        "--records-path",
        default=None,
        help="Dot path to records for nested JSON or mock API payloads.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        config = WorkflowConfig(
            input_path=Path(args.input_path),
            input_type=args.input_type,
            schema_path=Path(args.schema_path),
            output_dir=Path(args.output_dir),
            db_target=args.db_target,
            table_name=args.table_name,
            database_url=args.database_url,
            records_path=args.records_path,
        )

        report = run_workflow(config)

        print("Data quality ETL workflow completed.")
        print(f"Dataset: {report.dataset_name}")
        print(f"Input type: {report.input_type}")
        print(f"Raw rows: {report.row_count_raw}")
        print(f"Cleaned rows: {report.row_count_cleaned}")
        print(f"Issues: {len(report.issues)}")
        print(f"Database target: {config.db_target}")

        if config.db_target == "sqlite":
            print(f"Database output: {config.output_dir / 'etl_output.sqlite'}")
        elif config.db_target == "postgres":
            print(f"Database output: postgresql table: {config.table_name}")
        else:
            print("Database output: not exported")

        print(f"Report: {config.output_dir / 'quality_report.md'}")

        return 0

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())