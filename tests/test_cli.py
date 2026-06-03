from pathlib import Path

from dq_etl_starter.cli import main, run_workflow
from dq_etl_starter.models import WorkflowConfig


def test_run_workflow_csv(tmp_path):
    config = WorkflowConfig(
        input_path=Path("data/input/messy_customers.csv"),
        input_type="csv",
        schema_path=Path("data/expected/customer_schema.json"),
        output_dir=tmp_path,
        db_target="sqlite",
        table_name="cleaned_customers",
    )
    report = run_workflow(config)
    assert report.row_count_raw > report.row_count_cleaned
    assert (tmp_path / "cleaned_customers.csv").exists()
    assert (tmp_path / "etl_output.sqlite").exists()
    assert (tmp_path / "quality_report.md").exists()


def test_main_cli(tmp_path):
    exit_code = main([
        "run",
        "--input", "data/input/messy_customers.csv",
        "--input-type", "csv",
        "--schema", "data/expected/customer_schema.json",
        "--output-dir", str(tmp_path),
        "--db-target", "sqlite",
        "--table-name", "cleaned_customers",
    ])
    assert exit_code == 0
