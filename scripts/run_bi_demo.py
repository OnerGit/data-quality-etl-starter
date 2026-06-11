from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from time import perf_counter

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from dq_etl_starter.analytics import prepare_orders_for_analytics  # noqa: E402
from dq_etl_starter.bi import (  # noqa: E402
    build_reporting_tables,
    create_reporting_views,
    export_reporting_tables_to_postgres,
    validate_bi_outputs,
    write_bi_summary_report,
    write_metabase_dashboard_notes,
    write_reporting_queries,
)
from dq_etl_starter.clean import clean_dataframe  # noqa: E402
from dq_etl_starter.readers import read_csv_file  # noqa: E402
from dq_etl_starter.services import load_schema  # noqa: E402
from dq_etl_starter.validate import validate_schema  # noqa: E402


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the v0.5 BI-ready reporting demo from generated order data."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Generated input CSV path, for example data/generated/orders_100k.csv.",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        required=True,
        help="Schema file, for example data/expected/generated_order_schema.json.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/output/bi"),
        help="BI demo output directory.",
    )
    parser.add_argument(
        "--db-url",
        default=os.getenv("DATABASE_URL"),
        help=(
            "PostgreSQL SQLAlchemy URL. If omitted, DATABASE_URL is used. "
            "Example: postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo"
        ),
    )
    return parser


def run_demo(
    *,
    input_path: Path,
    schema_path: Path,
    output_dir: Path,
    database_url: str,
) -> dict[str, str]:
    start_time = perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)

    schema = load_schema(schema_path)
    raw_df = read_csv_file(input_path)
    _missing_expected, _unexpected_columns, issues = validate_schema(raw_df, schema)
    cleaned_df = clean_dataframe(raw_df)
    analytics_df = prepare_orders_for_analytics(cleaned_df)

    reporting_tables = build_reporting_tables(analytics_df)
    table_row_counts = export_reporting_tables_to_postgres(
        reporting_tables,
        database_url,
        if_exists="replace",
    )
    view_names = create_reporting_views(database_url)

    queries_path = write_reporting_queries(output_dir)
    metabase_notes_path = write_metabase_dashboard_notes(output_dir)

    runtime_seconds = perf_counter() - start_time
    output_files: dict[str, str] = {
        "reporting_queries_sql": str(queries_path),
        "metabase_dashboard_notes_md": str(metabase_notes_path),
    }

    table_previews = {
        "revenue_by_country": reporting_tables["revenue_by_country"],
        "orders_by_month": reporting_tables["orders_by_month"],
        "source_system_summary": reporting_tables["source_system_summary"],
    }

    summary_report_path = write_bi_summary_report(
        output_dir / "bi_summary_report.md",
        input_path=input_path,
        database_url=database_url,
        metrics={
            "row_count_raw": len(raw_df),
            "row_count_cleaned": len(cleaned_df),
            "row_count_analytics": len(analytics_df),
            "validation_issue_count": len(issues),
            "runtime_seconds": runtime_seconds,
        },
        table_row_counts=table_row_counts,
        view_names=view_names,
        output_files=output_files,
        table_previews=table_previews,
    )
    output_files["bi_summary_report_md"] = str(summary_report_path)

    validate_bi_outputs(
        output_files=output_files,
        table_row_counts=table_row_counts,
        view_names=view_names,
    )

    print("v0.5 BI-ready reporting demo completed")
    print("=" * 60)
    print(f"Input file: {input_path}")
    print(f"Schema file: {schema_path}")
    print(f"Output directory: {output_dir}")
    print("PostgreSQL reporting database: configured")
    print()
    print("Run summary")
    print("-" * 60)
    print(f"Input rows: {len(raw_df):,}")
    print(f"Cleaned rows: {len(cleaned_df):,}")
    print(f"Analytics-ready rows: {len(analytics_df):,}")
    print(f"Validation issues: {len(issues):,}")
    print(f"Runtime seconds: {runtime_seconds:.3f}")
    print()
    print("Reporting tables")
    print("-" * 60)
    for table_name, row_count in table_row_counts.items():
        print(f"- {table_name}: {row_count:,} rows")
    print()
    print("Reporting views")
    print("-" * 60)
    for view_name in view_names:
        print(f"- {view_name}")
    print()
    print("BI output files")
    print("-" * 60)
    for name, path in output_files.items():
        print(f"- {name}: {path}")
    print()
    print("Done.")

    return output_files


def main() -> None:
    args = build_arg_parser().parse_args()
    if not args.db_url:
        raise SystemExit(
            "PostgreSQL database URL is required. Pass --db-url or set DATABASE_URL."
        )

    run_demo(
        input_path=args.input,
        schema_path=args.schema,
        output_dir=args.output_dir,
        database_url=args.db_url,
    )


if __name__ == "__main__":
    main()
