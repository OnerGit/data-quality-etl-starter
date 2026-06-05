# Workflow

This project is designed around a small but complete data workflow:

```text
messy input data
-> read
-> flatten if needed
-> normalize columns
-> validate schema rules
-> clean text and duplicates
-> export cleaned data
-> generate quality report
```

## Why this is a workflow, not just a script

A one-off script can clean one file once. A workflow makes the process repeatable and easier to hand off.

This starter separates the steps into modules so each part can be tested and replaced:

- `readers.py`: load local CSV, Excel, and JSON files;
- `mock_api.py`: simulate API-style JSON without real network calls;
- `normalize.py`: normalize column names and flatten JSON;
- `validate.py`: check expected columns, missing values, duplicates, and simple schema rules;
- `clean.py`: trim whitespace, standardize selected fields, and drop duplicates;
- `exporters.py`: export cleaned data to CSV, SQLite, or optional PostgreSQL;
- `report.py`: build Markdown and JSON reports;
- `services.py`: provide shared workflow functions used by CLI and API entry points;
- `cli.py`: expose the workflow as a runnable command;
- `api.py`: expose the validation workflow as an optional FastAPI service layer.

The CLI remains the source of truth. The FastAPI layer added in v0.3 is a wrapper around the same shared workflow functions, not a separate implementation.

## Input paths

The workflow supports:

| Input type | Example input | Main capability shown |
|---|---|---|
| CSV | `data/input/messy_customers.csv` | Spreadsheet-style customer data cleaning. |
| Excel | `data/input/messy_orders.xlsx` | Excel export ingestion. |
| JSON | `data/input/nested_customers.json` | Nested JSON flattening. |
| mock API | `data/input/mock_api_orders.json` | API-style payload extraction without network calls. |

The CLI supports all four input types. The v0.3 API `/validate` endpoint supports uploaded `csv`, `excel`, and `json` files.

## Output paths

For local testing and screenshots, use separate output folders:

```text
data/output/csv/
data/output/excel/
data/output/json/
data/output/mock_api/
data/output/postgres/
data/output/api_runs/
```

This avoids overwriting `quality_report.md` when different input workflows are run one after another.

## Validation report row numbers

The validation report uses source-oriented row numbers for CSV-style inputs. The header row is counted as line 1, so a warning on `Row 6` means the issue appears on line 6 in the source CSV file.

This is intentional for handoff work because a client can open the original file and go directly to the reported source line.

## CLI workflow path

```text
CSV / Excel / JSON / mock API
-> read / flatten
-> normalize columns
-> validate expected schema rules
-> clean duplicate rows and text values
-> export cleaned CSV
-> export to SQLite by default or PostgreSQL optionally
-> generate Markdown and JSON quality reports
```

## API validation path

```text
CSV / Excel / JSON file upload
-> FastAPI /validate endpoint
-> save uploaded files to a temporary local folder
-> call the shared validation workflow
-> return Pydantic-based quality report JSON
-> optionally save report files under data/output/api_runs/
```

The default `/validate` behavior does not write cleaned CSV output and does not export to SQLite or PostgreSQL. That keeps the API endpoint focused on validation and report JSON.

## Screenshot story

For GitHub, Dev.to, and Upwork portfolio use, capture screenshots in this order:

1. show the messy input file;
2. show the CLI command running;
3. show the generated quality report;
4. show the cleaned CSV output;
5. show passing pytest tests;
6. show Docker running the workflow;
7. show nested JSON flattened into a table;
8. show optional PostgreSQL export;
9. show FastAPI Swagger UI;
10. show `/validate` response JSON.

Future screenshots after v0.3 may cover larger generated data, analytics-ready export, or BI-ready optional demos, but those are intentionally out of scope for v0.3.
