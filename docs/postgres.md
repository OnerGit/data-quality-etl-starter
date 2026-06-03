# Optional PostgreSQL Export

PostgreSQL is not required for the default v0.1 workflow. SQLite remains the default path because it is local and portable.

Use PostgreSQL when a client wants cleaned data loaded into a shared database or when the workflow needs to connect to an existing reporting database.

## Start local PostgreSQL

```bash
docker compose up -d postgres
```

## Run the workflow with PostgreSQL

```bash
DATABASE_URL=postgresql+psycopg://dq_user:dq_password@localhost:5432/dq_demo python -m dq_etl_starter.cli run   --input data/input/messy_customers.csv   --input-type csv   --schema data/expected/customer_schema.json   --output-dir data/output   --db-target postgres   --table-name cleaned_customers
```

## Why PostgreSQL is optional

The project is a lightweight data workflow starter, not a production warehouse. PostgreSQL strengthens the portfolio for clients who need database exports, but it should not make the default path harder to run.
