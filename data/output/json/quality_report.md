# Data Quality Report: customers

## Summary

- Input: `data\input\nested_customers.json`
- Input type: `json`
- Output table: `cleaned_customers_json`
- Raw rows: `2`
- Cleaned rows: `2`
- Columns: `6`
- Duplicate rows in raw input: `0` (0.00%)

## Columns

| Column | Missing values | Missing ratio |
|---|---:|---:|
| `customer_id` | 0 | 0.00% |
| `full_name` | 0 | 0.00% |
| `profile_email` | 0 | 0.00% |
| `profile_signup_date` | 0 | 0.00% |
| `address_country` | 0 | 0.00% |
| `metrics_revenue` | 1 | 50.00% |

## Expected Column Check

- Missing expected columns: `['country', 'email', 'revenue', 'signup_date']`
- Unexpected columns: `['address_country', 'metrics_revenue', 'profile_email', 'profile_signup_date']`

## Validation Issues

| Severity | Code | Column | Row | Value | Message |
|---|---|---|---:|---|---|
| error | `MISSING_EXPECTED_COLUMN` | `country` |  | `` | Expected column 'country' is missing from the input dataset. |
| error | `MISSING_EXPECTED_COLUMN` | `email` |  | `` | Expected column 'email' is missing from the input dataset. |
| error | `MISSING_EXPECTED_COLUMN` | `revenue` |  | `` | Expected column 'revenue' is missing from the input dataset. |
| error | `MISSING_EXPECTED_COLUMN` | `signup_date` |  | `` | Expected column 'signup_date' is missing from the input dataset. |
| warning | `UNEXPECTED_COLUMN` | `address_country` |  | `` | Column 'address_country' was found but is not listed in the expected schema. |
| warning | `UNEXPECTED_COLUMN` | `metrics_revenue` |  | `` | Column 'metrics_revenue' was found but is not listed in the expected schema. |
| warning | `UNEXPECTED_COLUMN` | `profile_email` |  | `` | Column 'profile_email' was found but is not listed in the expected schema. |
| warning | `UNEXPECTED_COLUMN` | `profile_signup_date` |  | `` | Column 'profile_signup_date' was found but is not listed in the expected schema. |
| error | `REQUIRED_COLUMN_NOT_FOUND` | `email` |  | `` | Required column 'email' is missing. |

## Output Files

- cleaned_csv: `data\output\json\cleaned_customers_json.csv`
- sqlite: `data\output\json\etl_output.sqlite`
