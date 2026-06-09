from __future__ import annotations

import argparse
import sys
from pathlib import Path
from time import perf_counter

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from dq_etl_starter.analytics import (  # noqa: E402
    prepare_orders_for_analytics,
    run_duckdb_queries,
    write_analytics_queries,
    write_benchmark_report,
    write_summary_tables,
)
from dq_etl_starter.clean import clean_dataframe  # noqa: E402
from dq_etl_starter.exporters import export_cleaned_csv, export_to_parquet  # noqa: E402
from dq_etl_starter.readers import read_csv_file  # noqa: E402
from dq_etl_starter.services import load_schema  # noqa: E402
from dq_etl_starter.validate import validate_schema  # noqa: E402


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the v0.4 analytics-ready export demo from generated order data."
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
        default=Path("data/output/analytics"),
        help="Analytics output directory.",
    )
    parser.add_argument(
        "--duckdb-preview-limit",
        type=int,
        default=10,
        help="Number of rows to print from the DuckDB preview query.",
    )
    return parser


def run_demo(
    input_path: Path,
    schema_path: Path,
    output_dir: Path,
    duckdb_preview_limit: int = 10,
) -> dict[str, str]:
    start_time = perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)

    schema = load_schema(schema_path)
    raw_df = read_csv_file(input_path)

    _missing_expected, _unexpected_columns, issues = validate_schema(raw_df, schema)

    cleaned_df = clean_dataframe(raw_df)
    analytics_df = prepare_orders_for_analytics(cleaned_df)

    cleaned_csv_path = export_cleaned_csv(
        analytics_df,
        output_dir / "cleaned_orders.csv",
    )
    parquet_path = export_to_parquet(
        analytics_df,
        output_dir / "cleaned_orders.parquet",
    )
    summary_files = write_summary_tables(analytics_df, output_dir)
    queries_path = write_analytics_queries(output_dir, parquet_path)
    duckdb_preview = run_duckdb_queries(parquet_path, limit=duckdb_preview_limit)

    runtime_seconds = perf_counter() - start_time

    output_files: dict[str, str] = {
        "cleaned_orders_csv": str(cleaned_csv_path),
        "cleaned_orders_parquet": str(parquet_path),
        **summary_files,
        "analytics_queries_sql": str(queries_path),
    }

    benchmark_path = write_benchmark_report(
        output_dir / "benchmark_report.md",
        input_path=input_path,
        metrics={
            "row_count_raw": len(raw_df),
            "row_count_cleaned": len(cleaned_df),
            "row_count_analytics": len(analytics_df),
            "validation_issue_count": len(issues),
            "runtime_seconds": runtime_seconds,
        },
        output_files=output_files,
        duckdb_preview=duckdb_preview,
    )
    output_files["benchmark_report_md"] = str(benchmark_path)

    print("v0.4 analytics-ready export completed")
    print("=" * 56)
    print(f"Input file: {input_path}")
    print(f"Schema file: {schema_path}")
    print(f"Output directory: {output_dir}")
    print()
    print("Run summary")
    print("-" * 56)
    print(f"Input rows: {len(raw_df):,}")
    print(f"Cleaned rows: {len(cleaned_df):,}")
    print(f"Analytics-ready rows: {len(analytics_df):,}")
    print(f"Validation issues: {len(issues):,}")
    print(f"Runtime seconds: {runtime_seconds:.3f}")
    print()
    print("Analytics output files")
    print("-" * 56)
    for name, path in output_files.items():
        print(f"- {name}: {path}")
    print()
    print("DuckDB preview query")
    print("-" * 56)
    print(f"Source Parquet: {parquet_path}")
    print(f"SQL saved to: {queries_path}")
    print()
    print(duckdb_preview.to_string(index=False))
    print()
    print("Done.")

    return output_files


def main() -> None:
    args = build_arg_parser().parse_args()
    run_demo(
        input_path=args.input,
        schema_path=args.schema,
        output_dir=args.output_dir,
        duckdb_preview_limit=args.duckdb_preview_limit,
    )


if __name__ == "__main__":
    main()