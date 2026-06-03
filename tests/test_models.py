from pathlib import Path

from dq_etl_starter.cli import load_schema
from dq_etl_starter.models import WorkflowConfig


def test_load_customer_schema():
    schema = load_schema(Path("data/expected/customer_schema.json"))
    assert schema.dataset_name == "customers"
    assert "email" in schema.rules_by_name


def test_workflow_config_rejects_bad_table_name(tmp_path):
    try:
        WorkflowConfig(
            input_path=Path("data/input/messy_customers.csv"),
            input_type="csv",
            schema_path=Path("data/expected/customer_schema.json"),
            output_dir=tmp_path,
            table_name="bad table name!",
        )
    except ValueError as exc:
        assert "table_name" in str(exc)
    else:
        raise AssertionError("Expected invalid table name to raise ValueError")
