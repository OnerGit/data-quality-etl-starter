from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from dq_etl_starter.models import ApiErrorResponse, HealthResponse, QualityReport, WorkflowConfig
from dq_etl_starter.services import validate_file_workflow

API_VERSION = "0.3.0"
SERVICE_NAME = "data-quality-etl-starter-api"
SUPPORTED_VALIDATE_INPUT_TYPES = {"csv", "excel", "json"}

app = FastAPI(
    title="Data Quality ETL Starter API",
    description=(
        "Optional FastAPI validation service layer around the existing "
        "data quality ETL workflow. The CLI remains the source of truth."
    ),
    version=API_VERSION,
)


def _suffix_for_upload(filename: str | None, input_type: str) -> str:
    suffix = Path(filename or "").suffix
    if suffix:
        return suffix
    if input_type == "csv":
        return ".csv"
    if input_type == "excel":
        return ".xlsx"
    if input_type == "json":
        return ".json"
    return ".data"


async def _save_upload(upload: UploadFile, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    await upload.close()
    return output_path


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        version=API_VERSION,
    )


@app.post(
    "/validate",
    response_model=QualityReport,
    responses={400: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
)
async def validate_upload(
    file: UploadFile = File(..., description="CSV, Excel, or JSON file to validate."),
    input_type: str = Form(..., description="One of: csv, excel, json."),
    schema_file: UploadFile | None = File(
        default=None,
        description="JSON schema file using this project's DatasetSchema format.",
    ),
    records_path: str | None = Form(
        default=None,
        description="Optional dot path for nested JSON records, for example data.customers.",
    ),
    save_report: bool = Form(
        default=False,
        description="If true, save quality_report.md and quality_report.json under data/output/api_runs/.",
    ),
) -> QualityReport:
    normalized_input_type = input_type.strip().lower()
    if normalized_input_type not in SUPPORTED_VALIDATE_INPUT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported input_type. Supported values are: csv, excel, json.",
        )

    if schema_file is None:
        raise HTTPException(
            status_code=400,
            detail="schema_file is required.",
        )

    run_id = uuid4().hex[:12]
    persistent_output_dir = Path("data/output/api_runs") / run_id

    try:
        with tempfile.TemporaryDirectory(prefix="dq_etl_api_") as temp_dir_raw:
            temp_dir = Path(temp_dir_raw)
            input_path = temp_dir / f"input{_suffix_for_upload(file.filename, normalized_input_type)}"
            schema_path = temp_dir / "schema.json"

            await _save_upload(file, input_path)
            await _save_upload(schema_file, schema_path)

            config = WorkflowConfig(
                input_path=input_path,
                input_type=normalized_input_type,
                schema_path=schema_path,
                output_dir=persistent_output_dir if save_report else temp_dir / "output",
                db_target="none",
                table_name="api_validated_data",
                records_path=records_path,
            )

            return validate_file_workflow(
                config,
                save_report=save_report,
            )
    except HTTPException:
        raise
    except (ValidationError, ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - safety net for unexpected runtime failures
        raise HTTPException(
            status_code=500,
            detail=f"Validation workflow failed: {exc}",
        ) from exc
