# Pydantic Schema Design

Pydantic is used for stable workflow contracts:

- runtime configuration;
- dataset schema rules;
- validation issues;
- quality report output.

It is not used to hardcode every row in a dynamic CSV, Excel, JSON, or API-style input file. Freelance client data often changes columns between exports, so the row-level cleaning stays DataFrame-based.

## Example schema

```json
{
  "dataset_name": "customers",
  "expected_columns": [
    "customer_id",
    "full_name",
    "email",
    "signup_date",
    "country",
    "revenue"
  ],
  "column_rules": [
    {
      "name": "customer_id",
      "dtype": "string",
      "required": true,
      "allow_missing": false
    },
    {
      "name": "email",
      "dtype": "email",
      "required": true,
      "allow_missing": false
    },
    {
      "name": "signup_date",
      "dtype": "date",
      "required": false,
      "allow_missing": true
    },
    {
      "name": "revenue",
      "dtype": "number",
      "required": false,
      "allow_missing": true
    }
  ]
}
```

## Design boundary

Pydantic is a good fit for stable metadata and validation contracts. pandas remains responsible for flexible tabular processing because incoming client datasets are often not known in advance.
