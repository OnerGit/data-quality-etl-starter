from __future__ import annotations

from pathlib import Path

from dq_etl_starter.clean import clean_dataframe
from dq_etl_starter.mock_api import mock_api_response_to_dataframe
from dq_etl_starter.models import DatasetSchema, QualityReport, WorkflowConfig
from dq_etl_starter.readers import read_csv_file, read_excel_file, read_json_file
from dq_etl_starter.report import (
    build_quality_report,
    export_report_json,
    export_report_markdown,
)
from dq_etl_starter.validate import validate_schema


def load_schema(path: str | Path) -> DatasetSchema:
    """Load the expected dataset schema from a JSON file."""
    return DatasetSchema.model_validate_json(Path(path).read_text(encoding="utf-8"))


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


def _export_cleaned_outputs(config: WorkflowConfig, cleaned_df) -> dict[str, str]:
    """Export cleaned data to CSV and the configured database target."""
    # Keep exporter imports inside the export path so the lightweight API
    # validation path does not need to import database connectors at startup.
    from dq_etl_starter.exporters import (
        export_cleaned_csv,
        export_to_postgres,
        export_to_sqlite,
    )

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

    return output_files


def build_workflow_report(
    config: WorkflowConfig,
    *,
    export_outputs: bool,
    save_report: bool,
) -> QualityReport:
    """Build a quality report by reusing the same read/validate/clean workflow.

    CLI calls this with export_outputs=True and save_report=True.
    The FastAPI /validate endpoint calls this with export_outputs=False by default,
    so it can return a report JSON without writing cleaned data or touching a DB.
    """
    config.output_dir.mkdir(parents=True, exist_ok=True)

    schema = load_schema(config.schema_path)
    raw_df = read_input(config)
    missing_expected, unexpected, issues = validate_schema(raw_df, schema)
    cleaned_df = clean_dataframe(raw_df)

    output_files: dict[str, str] = {}
    if export_outputs:
        output_files.update(_export_cleaned_outputs(config, cleaned_df))
    else:
        output_files["database"] = "not exported"

    report_md_path = config.output_dir / "quality_report.md"
    report_json_path = config.output_dir / "quality_report.json"

    if save_report:
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

    if save_report:
        export_report_markdown(report, report_md_path)
        export_report_json(report, report_json_path)

    return report


def run_workflow(config: WorkflowConfig) -> QualityReport:
    """Run the complete CLI data quality ETL workflow."""
    return build_workflow_report(
        config,
        export_outputs=True,
        save_report=True,
    )


def validate_file_workflow(
    config: WorkflowConfig,
    *,
    save_report: bool = False,
) -> QualityReport:
    """Run validation and report generation for the FastAPI service layer."""
    return build_workflow_report(
        config,
        export_outputs=False,
        save_report=save_report,
    )
