from __future__ import annotations

from pathlib import Path

import pandas as pd

from dq_etl_starter.models import DatasetSchema, QualityReport, ValidationIssue, WorkflowConfig
from dq_etl_starter.validate import find_duplicates, find_missing_values


def build_quality_report(
    *,
    config: WorkflowConfig,
    schema: DatasetSchema,
    raw_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    missing_expected_columns: list[str],
    unexpected_columns: list[str],
    issues: list[ValidationIssue],
    output_files: dict[str, str],
) -> QualityReport:
    missing_counts, missing_ratios = find_missing_values(raw_df)
    duplicate_count, duplicate_ratio = find_duplicates(raw_df)
    return QualityReport(
        dataset_name=schema.dataset_name,
        input_path=str(config.input_path),
        input_type=config.input_type,
        table_name=config.table_name,
        row_count_raw=len(raw_df),
        row_count_cleaned=len(cleaned_df),
        column_count=len(raw_df.columns),
        column_names=list(raw_df.columns),
        expected_columns=schema.expected_columns,
        missing_expected_columns=missing_expected_columns,
        unexpected_columns=unexpected_columns,
        missing_values_by_column=missing_counts,
        missing_value_ratio_by_column={column: round(value, 4) for column, value in missing_ratios.items()},
        duplicate_row_count=duplicate_count,
        duplicate_row_ratio=round(duplicate_ratio, 4),
        issues=issues,
        output_files=output_files,
    )


def render_markdown_report(report: QualityReport) -> str:
    lines: list[str] = []
    lines.append(f"# Data Quality Report: {report.dataset_name}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Input: `{report.input_path}`")
    lines.append(f"- Input type: `{report.input_type}`")
    lines.append(f"- Output table: `{report.table_name}`")
    lines.append(f"- Raw rows: `{report.row_count_raw}`")
    lines.append(f"- Cleaned rows: `{report.row_count_cleaned}`")
    lines.append(f"- Columns: `{report.column_count}`")
    lines.append(f"- Duplicate rows in raw input: `{report.duplicate_row_count}` ({report.duplicate_row_ratio:.2%})")
    lines.append("")

    lines.append("## Columns")
    lines.append("")
    lines.append("| Column | Missing values | Missing ratio |")
    lines.append("|---|---:|---:|")
    for column in report.column_names:
        count = report.missing_values_by_column.get(column, 0)
        ratio = report.missing_value_ratio_by_column.get(column, 0.0)
        lines.append(f"| `{column}` | {count} | {ratio:.2%} |")
    lines.append("")

    lines.append("## Expected Column Check")
    lines.append("")
    lines.append(f"- Missing expected columns: `{report.missing_expected_columns or []}`")
    lines.append(f"- Unexpected columns: `{report.unexpected_columns or []}`")
    lines.append("")

    lines.append("## Validation Issues")
    lines.append("")
    if report.issues:
        lines.append("| Severity | Code | Column | Row | Value | Message |")
        lines.append("|---|---|---|---:|---|---|")
        for issue in report.issues:
            lines.append(
                f"| {issue.severity} | `{issue.code}` | `{issue.column or ''}` | "
                f"{issue.row_number or ''} | `{issue.value or ''}` | {issue.message} |"
            )
    else:
        lines.append("No validation issues found.")
    lines.append("")

    lines.append("## Output Files")
    lines.append("")
    for name, path in report.output_files.items():
        lines.append(f"- {name}: `{path}`")
    lines.append("")
    return "\n".join(lines)


def export_report_markdown(report: QualityReport, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown_report(report), encoding="utf-8")
    return output_path


def export_report_json(report: QualityReport, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return output_path
