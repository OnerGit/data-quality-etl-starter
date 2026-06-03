# Data Quality Report: orders

## Summary

- Input: `data\input\messy_orders.xlsx`
- Input type: `excel`
- Output table: `cleaned_orders`
- Raw rows: `4`
- Cleaned rows: `3`
- Columns: `5`
- Duplicate rows in raw input: `1` (25.00%)

## Columns

| Column | Missing values | Missing ratio |
|---|---:|---:|
| `order_id` | 0 | 0.00% |
| `customer_id` | 0 | 0.00% |
| `order_date` | 0 | 0.00% |
| `amount` | 1 | 25.00% |
| `status` | 0 | 0.00% |

## Expected Column Check

- Missing expected columns: `[]`
- Unexpected columns: `[]`

## Validation Issues

| Severity | Code | Column | Row | Value | Message |
|---|---|---|---:|---|---|
| warning | `INVALID_DATE` | `order_date` | 4 | `bad-date` | Value 'bad-date' cannot be parsed as a date. |
| warning | `INVALID_DATE` | `order_date` | 5 | `bad-date` | Value 'bad-date' cannot be parsed as a date. |

## Output Files

- cleaned_csv: `data\output\excel\cleaned_orders.csv`
- sqlite: `data\output\excel\etl_output.sqlite`
