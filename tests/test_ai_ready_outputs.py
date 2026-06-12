from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

from dq_etl_starter.ai_ready import (
    build_ai_ready_manifest,
    validate_ai_ready_outputs,
    write_ai_ready_summary_report,
    write_json,
)


def _load_run_ai_ready_demo():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "run_ai_ready_demo.py"
    spec = importlib.util.spec_from_file_location(
        "run_ai_ready_demo_module",
        script_path,
    )

    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load script module from {script_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module.run_ai_ready_demo


def test_write_ai_ready_summary_report(tmp_path: Path) -> None:
    output_files = {
        "schema_profile": "schema_profile.json",
        "data_dictionary": "data_dictionary.json",
        "validation_summary": "validation_summary.json",
        "feature_ready_dataset": "feature_ready_orders.csv",
        "embedding_ready_text_fields": "embedding_ready_text_fields.csv",
        "ai_ready_manifest": "ai_ready_manifest.json",
    }
    manifest = build_ai_ready_manifest(outputs=output_files)

    report_path = write_ai_ready_summary_report(
        tmp_path / "ai_ready_summary_report.md",
        dataset_name="cleaned_orders",
        row_count=2,
        output_files=output_files,
        manifest=manifest,
    )

    content = report_path.read_text(encoding="utf-8")
    assert "# AI-ready Data Preparation Summary" in content
    assert "No LLM API was called." in content
    assert "No embeddings were generated." in content
    assert "No model was trained." in content


def test_validate_ai_ready_outputs_detects_missing_files(tmp_path: Path) -> None:
    is_valid, missing_files = validate_ai_ready_outputs(tmp_path)

    assert is_valid is False
    assert "schema_profile.json" in missing_files
    assert "ai_ready_manifest.json" in missing_files


def test_validate_ai_ready_outputs_passes_when_files_exist(tmp_path: Path) -> None:
    filenames = [
        "schema_profile.json",
        "data_dictionary.json",
        "validation_summary.json",
        "feature_ready_orders.csv",
        "embedding_ready_text_fields.csv",
        "ai_ready_manifest.json",
        "ai_ready_summary_report.md",
    ]
    for filename in filenames:
        (tmp_path / filename).write_text("ok\n", encoding="utf-8")

    is_valid, missing_files = validate_ai_ready_outputs(tmp_path)

    assert is_valid is True
    assert missing_files == []


def test_write_json_outputs_stable_json(tmp_path: Path) -> None:
    output_path = write_json({"llm_api_called": False}, tmp_path / "manifest.json")
    loaded = json.loads(output_path.read_text(encoding="utf-8"))

    assert loaded["llm_api_called"] is False


def test_run_ai_ready_demo_with_small_input(tmp_path: Path) -> None:
    run_ai_ready_demo = _load_run_ai_ready_demo()

    input_path = tmp_path / "orders.csv"
    schema_path = tmp_path / "schema.json"
    output_dir = tmp_path / "ai_ready"

    pd.DataFrame(
        [
            {
                "order_id": "ORD-000001",
                "customer_id": "CUS-0001",
                "order_date": "2026-01-01",
                "country": "United States",
                "product_category": "Electronics",
                "quantity": 2,
                "unit_price": 100.0,
                "discount_rate": 0.1,
                "revenue": 180.0,
                "email": "alice@example.com",
                "source_system": "web",
            },
            {
                "order_id": "ORD-000002",
                "customer_id": "CUS-0002",
                "order_date": "2026-01-02",
                "country": "Singapore",
                "product_category": "Office",
                "quantity": 1,
                "unit_price": 50.0,
                "discount_rate": 0.0,
                "revenue": 50.0,
                "email": "bob@example.com",
                "source_system": "api",
            },
        ]
    ).to_csv(input_path, index=False)

    schema_path.write_text(
        json.dumps(
            {
                "dataset_name": "generated_orders",
                "expected_columns": [
                    "order_id",
                    "customer_id",
                    "order_date",
                    "country",
                    "product_category",
                    "quantity",
                    "unit_price",
                    "discount_rate",
                    "revenue",
                    "email",
                    "source_system",
                ],
                "column_rules": [
                    {"name": "order_id", "dtype": "string", "required": True, "allow_missing": False},
                    {"name": "customer_id", "dtype": "string", "required": True, "allow_missing": False},
                    {"name": "order_date", "dtype": "date", "required": True, "allow_missing": False},
                    {"name": "country", "dtype": "string", "required": True, "allow_missing": False},
                    {"name": "product_category", "dtype": "string", "required": True, "allow_missing": False},
                    {"name": "quantity", "dtype": "number", "required": True, "allow_missing": False},
                    {"name": "unit_price", "dtype": "number", "required": True, "allow_missing": False},
                    {"name": "discount_rate", "dtype": "number", "required": True, "allow_missing": False},
                    {"name": "revenue", "dtype": "number", "required": True, "allow_missing": False},
                    {"name": "email", "dtype": "email", "required": True, "allow_missing": False},
                    {"name": "source_system", "dtype": "string", "required": True, "allow_missing": False},
                ],
            }
        ),
        encoding="utf-8",
    )

    outputs = run_ai_ready_demo(
        input_path=input_path,
        schema_path=schema_path,
        output_dir=output_dir,
        dataset_name="cleaned_orders",
    )

    assert Path(outputs["schema_profile"]).exists()
    assert Path(outputs["data_dictionary"]).exists()
    assert Path(outputs["validation_summary"]).exists()
    assert Path(outputs["feature_ready_dataset"]).exists()
    assert Path(outputs["embedding_ready_text_fields"]).exists()
    assert Path(outputs["ai_ready_manifest"]).exists()

    manifest = json.loads(Path(outputs["ai_ready_manifest"]).read_text(encoding="utf-8"))
    assert manifest["llm_api_called"] is False
    assert manifest["embedding_generated"] is False
    assert manifest["model_trained"] is False
