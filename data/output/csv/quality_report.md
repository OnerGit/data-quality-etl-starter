# Data Quality Report: customers

## Summary

- Input: `data\input\messy_customers.csv`
- Input type: `csv`
- Output table: `cleaned_customers`
- Raw rows: `5`
- Cleaned rows: `4`
- Columns: `6`
- Duplicate rows in raw input: `1` (20.00%)

## Columns

| Column | Missing values | Missing ratio |
|---|---:|---:|
| `customer_id` | 0 | 0.00% |
| `full_name` | 0 | 0.00% |
| `email` | 1 | 20.00% |
| `signup_date` | 0 | 0.00% |
| `country` | 0 | 0.00% |
| `revenue` | 1 | 20.00% |

## Expected Column Check

- Missing expected columns: `[]`
- Unexpected columns: `[]`

## Validation Issues

| Severity | Code | Column | Row | Value | Message |
|---|---|---|---:|---|---|
| warning | `MISSING_REQUIRED_VALUE` | `email` | 3 | `` | Column 'email' has a missing required value. |
| warning | `INVALID_EMAIL` | `email` | 4 | `bad-email` | Value 'bad-email' is not a valid email format. |
| warning | `INVALID_EMAIL` | `email` | 6 | `bad-email` | Value 'bad-email' is not a valid email format. |
| warning | `INVALID_DATE` | `signup_date` | 5 | `not-a-date` | Value 'not-a-date' cannot be parsed as a date. |
| warning | `INVALID_NUMBER` | `revenue` | 5 | `not-a-number` | Value 'not-a-number' cannot be parsed as a number. |

## Output Files

- cleaned_csv: `data\output\csv\cleaned_customers.csv`
- sqlite: `data\output\csv\etl_output.sqlite`
