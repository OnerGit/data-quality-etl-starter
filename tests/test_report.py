import pandas as pd

from dq_etl_starter.models import DatasetSchema, WorkflowConfig
from dq_etl_starter.report import build_quality_report, render_markdown_report


def test_render_markdown_report(tmp_path):
    config = WorkflowConfig(
        input_path="input.csv",
        input_type="csv",
        schema_path="schema.json",
        output_dir=tmp_path,
        table_name="cleaned_customers",
    )
    schema = DatasetSchema(dataset_name="customers", expected_columns=["email"], column_rules=[])
    raw_df = pd.DataFrame({"email": ["a@example.com", None]})
    cleaned_df = raw_df.copy()
    report = build_quality_report(
        config=config,
        schema=schema,
        raw_df=raw_df,
        cleaned_df=cleaned_df,
        missing_expected_columns=[],
        unexpected_columns=[],
        issues=[],
        output_files={"cleaned_csv": "out.csv"},
    )
    markdown = render_markdown_report(report)
    assert "Data Quality Report" in markdown
    assert "Missing ratio" in markdown
