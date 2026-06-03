FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

COPY requirements.txt pyproject.toml README.md ./
COPY src ./src
COPY data ./data
COPY docs ./docs

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "dq_etl_starter.cli", "run", "--input", "data/input/messy_customers.csv", "--input-type", "csv", "--schema", "data/expected/customer_schema.json", "--output-dir", "data/output", "--db-target", "sqlite", "--table-name", "cleaned_customers"]
