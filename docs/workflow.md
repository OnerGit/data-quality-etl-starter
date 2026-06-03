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
- `exporters.py`: export cleaned data;
- `report.py`: build Markdown and JSON reports;
- `cli.py`: connect the workflow into a runnable command.

## Screenshot story

For GitHub, Dev.to, and Upwork portfolio use, capture screenshots in this order:

1. Show the messy input file.
2. Show the CLI command running.
3. Show the generated quality report.
4. Show the cleaned CSV output.
5. Show passing pytest tests.
6. Show Docker running the workflow.
7. Optional: show PostgreSQL export.
8. Optional: show FastAPI Swagger UI after v0.3.
9. Optional: show `/validate` response after v0.3.
