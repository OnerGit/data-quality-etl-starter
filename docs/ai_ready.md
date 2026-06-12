# AI-ready Data Preparation

v0.6.0 adds an optional AI-ready data preparation demo.

This project does **not** call an LLM. Instead, it prepares cleaner, validated, documented, machine-readable data that can be used later for BI, ML, or AI workflows.

## Scope

AI-ready in this project means clean, validated, documented, and machine-readable data assets.

This demo produces:

- a schema profile JSON file;
- a data dictionary JSON file;
- a validation summary JSON file;
- a feature-ready CSV output;
- an embedding-ready text field extract;
- an AI-ready manifest JSON file;
- a Markdown summary report.

## What this demo does not do

This demo intentionally does not include:

- LLM API calls;
- OpenAI, Claude, Gemini, or other paid AI APIs;
- local LLM integration;
- embeddings generation;
- vector databases;
- RAG chatbots;
- AI agents;
- automatic SQL generation;
- automatic data cleaning by LLM;
- model training;
- AutoML;
- feature stores;
- MLflow or MLOps tooling;
- cloud deployment;
- custom frontend code.

The goal is data preparation and handoff, not AI application development.

## Workflow

The v0.6 optional workflow is:

```text
generated messy order data
    ↓
existing validation and cleaning workflow
    ↓
cleaned orders dataset
    ↓
schema profile JSON
    ↓
data dictionary JSON
    ↓
validation summary JSON
    ↓
feature-ready CSV
    ↓
embedding-ready text field extract
    ↓
AI-ready manifest + summary report
```

## Generate synthetic input data

macOS / Linux:

```bash
python scripts/generate_sample_data.py \
  --rows 100000 \
  --output data/generated/orders_100k.csv \
  --seed 42
```

Windows PowerShell:

```powershell
python scripts/generate_sample_data.py `
  --rows 100000 `
  --output data/generated/orders_100k.csv `
  --seed 42
```

The generated data is synthetic and local. It should not be treated as real customer data.

## Run the AI-ready demo

macOS / Linux:

```bash
python scripts/run_ai_ready_demo.py \
  --input data/generated/orders_100k.csv \
  --schema data/expected/generated_order_schema.json \
  --output-dir data/output/ai_ready \
  --dataset-name cleaned_orders
```

Windows PowerShell:

```powershell
python scripts/run_ai_ready_demo.py `
  --input data/generated/orders_100k.csv `
  --schema data/expected/generated_order_schema.json `
  --output-dir data/output/ai_ready `
  --dataset-name cleaned_orders
```

## Expected outputs

```text
data/output/ai_ready/
├── ai_ready_summary_report.md
├── ai_ready_manifest.json
├── data_dictionary.json
├── schema_profile.json
├── validation_summary.json
├── feature_ready_orders.csv
└── embedding_ready_text_fields.csv
```

## Output file guide

### `schema_profile.json`

A machine-readable profile of the cleaned dataset.

It includes:

- dataset name;
- row count;
- column count;
- column names;
- inferred dtypes;
- null counts and ratios;
- unique counts and ratios;
- example values;
- recommended column roles.

This file helps downstream users inspect data structure before using the dataset in BI, ML, or AI workflows.

### `data_dictionary.json`

A documented description of each column.

It includes:

- column name;
- human-readable description;
- type;
- recommended role;
- nullable flag;
- example values;
- usage notes.

This file is useful for handoff because it explains what each field means and how it should be treated.

### `validation_summary.json`

A compact machine-readable validation and cleaning summary.

It includes:

- source file;
- schema file;
- row count before cleaning;
- row count after preparation;
- duplicate rows removed;
- columns with missing values;
- validation issue count;
- validation issue codes;
- AI-readiness notes.

This file is useful for auditability and downstream data quality review.

### `feature_ready_orders.csv`

A simple feature-ready tabular output.

By default, it removes identifier and contact fields such as:

- `order_id`;
- `customer_id`;
- `email`.

It also converts `order_date` into simple time-based columns such as `order_year` and `order_month`.

This output is for downstream feature exploration. It does not train a model.

### `embedding_ready_text_fields.csv`

A text field extract for later optional embedding workflows.

It includes:

- `record_id`;
- `text`;
- `source_columns`.

This project does not generate embeddings. It only prepares text fields so another workflow can decide later whether embeddings are appropriate.

Contact fields such as `email` are excluded by default.

### `ai_ready_manifest.json`

A scope and output manifest.

It explicitly marks:

```json
{
  "llm_api_called": false,
  "embedding_generated": false,
  "model_trained": false
}
```

This file documents what the demo generated and what it intentionally kept out of scope.

### `ai_ready_summary_report.md`

A human-readable Markdown summary of the AI-ready data preparation run.

It includes:

- dataset name;
- prepared row count;
- generated output files;
- scope note;
- recommended downstream use;
- out-of-scope items.

## Check output files

Windows PowerShell:

```powershell
Get-ChildItem data/output/ai_ready
```

macOS / Linux:

```bash
ls -lah data/output/ai_ready
```

## Tests

Run the AI-ready tests:

```bash
pytest tests/test_ai_ready.py
pytest tests/test_ai_ready_outputs.py
```

Run the full test suite:

```bash
python -m compileall -q src/dq_etl_starter
python -m compileall -q scripts
pytest
```

The default tests do not require PostgreSQL, Metabase, external datasets, or any LLM API key.

## Docker compatibility

The default Docker workflow remains the existing simple CLI workflow.

The AI-ready demo is optional and can be run locally after generating synthetic input data.

## Local artifact policy

The following files are intentionally local artifacts and should not be committed:

```text
data/generated/
data/output/ai_ready/
data/output/analytics/
data/output/bi/
*.parquet
*.duckdb
metabase.db/
metabase-data/
postgres_data/
```

The repository should keep source code, tests, documentation, schemas, lightweight sample files, and screenshots.

## Real public dataset policy

Real public datasets can be useful for local validation, but they are not part of the default v0.6.0 workflow.

Do not commit:

- large raw public datasets;
- external downloaded datasets;
- large feature-ready outputs;
- real customer data;
- embedding vectors;
- model files;
- API keys or credentials.

If a real dataset is tested locally, document the source, license, access note, and validation result in a separate local report or a lightweight documentation note.

## Handoff guidance

These files can be handed off to later workflows as follows:

- BI users can inspect the schema profile, data dictionary, and validation summary before creating dashboards.
- ML users can start with the feature-ready CSV and review which fields were removed or transformed.
- AI/RAG users can inspect the embedding-ready text extract before deciding whether a separate embedding pipeline is appropriate.
- Data reviewers can use the manifest and validation summary to understand what was generated and what remained out of scope.

This project stops at documented data preparation. Downstream BI, ML, or AI workflows should make their own modeling, embedding, governance, and deployment decisions.
