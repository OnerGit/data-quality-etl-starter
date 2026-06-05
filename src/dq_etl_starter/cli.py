from __future__ import annotations

import argparse
from pathlib import Path

from dq_etl_starter.models import WorkflowConfig
from dq_etl_starter.services import load_schema, read_input, run_workflow


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
