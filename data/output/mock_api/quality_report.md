# Data Quality Report: orders

## Summary

- Input: `data\input\mock_api_orders.json`
- Input type: `mock-api`
- Output table: `cleaned_api_orders`
- Raw rows: `3`
- Cleaned rows: `2`
- Columns: `6`
- Duplicate rows in raw input: `1` (33.33%)

## Columns

| Column | Missing values | Missing ratio |
|---|---:|---:|
| `order_id` | 0 | 0.00% |
| `order_date` | 0 | 0.00% |
| `amount` | 2 | 66.67% |
| `customer_id` | 0 | 0.00% |
| `customer_email` | 0 | 0.00% |
| `shipping_country` | 0 | 0.00% |

## Expected Column Check

- Missing expected columns: `['status']`
- Unexpected columns: `['customer_email', 'shipping_country']`

## Validation Issues

| Severity | Code | Column | Row | Value | Message |
|---|---|---|---:|---|---|
| error | `MISSING_EXPECTED_COLUMN` | `status` |  | `` | Expected column 'status' is missing from the input dataset. |
| warning | `UNEXPECTED_COLUMN` | `customer_email` |  | `` | Column 'customer_email' was found but is not listed in the expected schema. |
| warning | `UNEXPECTED_COLUMN` | `shipping_country` |  | `` | Column 'shipping_country' was found but is not listed in the expected schema. |
| warning | `INVALID_EMAIL` | `customer_email` | 3 | `bad-api-email` | Value 'bad-api-email' is not a valid email format. |
| warning | `INVALID_EMAIL` | `customer_email` | 4 | `bad-api-email` | Value 'bad-api-email' is not a valid email format. |

## Output Files

- cleaned_csv: `data\output\mock_api\cleaned_api_orders.csv`
- sqlite: `data\output\mock_api\etl_output.sqlite`
