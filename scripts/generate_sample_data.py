from __future__ import annotations

import argparse
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

NORMALIZED_ORDER_COLUMNS = [
    "order_id",
    "customer_id",
    "order_date",
    "country",
    "product_category",
    "quantity",
    "unit_price",
    "discount_rate",
    "revenue",
    "email",
    "source_system",
]

MESSY_ORDER_COLUMN_NAMES = {
    "order_id": "Order ID",
    "customer_id": "Customer ID",
    "order_date": "Order Date",
    "country": "Country",
    "product_category": "Product Category",
    "quantity": "Quantity",
    "unit_price": "Unit Price",
    "discount_rate": "Discount Rate",
    "revenue": "Revenue",
    "email": "Email",
    "source_system": "Source System",
}

COUNTRIES = [
    "United States",
    "United Kingdom",
    "Singapore",
    "Canada",
    "Australia",
    "Germany",
    "France",
    "Japan",
]

PRODUCT_CATEGORIES = [
    "Software",
    "Hardware",
    "Office Supplies",
    "Training",
    "Consulting",
    "Subscription",
]

SOURCE_SYSTEMS = ["shopify", "stripe", "manual_csv", "legacy_crm", "partner_api"]


def _synthetic_email(customer_id: int) -> str:
    """Return a deterministic synthetic email address.

    The example.com domain is reserved for examples, so this does not create
    plausible real customer contact data.
    """

    return f"customer{customer_id:06d}@example.com"


def generate_orders_dataframe(
    rows: int,
    *,
    seed: int = 42,
    messy_column_names: bool = True,
    include_issues: bool = True,
) -> pd.DataFrame:
    """Generate deterministic synthetic customer/order-style data.

    This data is intentionally fake and is designed for ETL validation demos.
    It is not downloaded from an external source and does not contain real
    customer data.
    """

    if rows <= 0:
        raise ValueError("rows must be a positive integer")

    rng = random.Random(seed)
    base_date = date(2023, 1, 1)
    records: list[dict[str, object]] = []

    for index in range(rows):
        customer_id = rng.randint(1, max(50, rows // 8))
        order_date = base_date + timedelta(days=rng.randint(0, 730))
        country = rng.choice(COUNTRIES)
        category = rng.choice(PRODUCT_CATEGORIES)
        quantity = rng.randint(1, 8)
        unit_price = round(rng.uniform(8.0, 450.0), 2)
        discount_rate = rng.choice([0.0, 0.05, 0.1, 0.15, 0.2])
        revenue = round(quantity * unit_price * (1 - discount_rate), 2)

        record: dict[str, object] = {
            "order_id": f"ORD-{index + 1:08d}",
            "customer_id": f"CUST-{customer_id:06d}",
            "order_date": order_date.isoformat(),
            "country": country,
            "product_category": category,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount_rate": discount_rate,
            "revenue": revenue,
            "email": _synthetic_email(customer_id),
            "source_system": rng.choice(SOURCE_SYSTEMS),
        }

        if include_issues:
            # Intentional, deterministic data quality issues.
            if index % 37 == 0:
                record["email"] = ""
            if index % 53 == 0:
                record["email"] = f"invalid-email-{index}"
            if index % 41 == 0:
                record["country"] = ""
            if index % 29 == 0 and isinstance(record["country"], str):
                record["country"] = record["country"].lower()
            if index % 67 == 0:
                record["order_date"] = "not-a-date"
            if index % 71 == 0:
                record["quantity"] = -abs(int(record["quantity"]))
            if index % 83 == 0:
                record["unit_price"] = 0
                record["revenue"] = 0
            if index > 0 and index % 97 == 0:
                # Keep the requested row count while introducing a true full-row duplicate.
                record = records[-1].copy()

        records.append(record)

    df = pd.DataFrame(records, columns=NORMALIZED_ORDER_COLUMNS)
    if messy_column_names:
        df = df.rename(columns=MESSY_ORDER_COLUMN_NAMES)
    return df


def write_orders_csv(df: pd.DataFrame, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate deterministic synthetic order data for the v0.4 analytics demo."
    )
    parser.add_argument(
        "--rows",
        type=int,
        required=True,
        help="Number of rows to generate, for example 1000, 10000, or 100000.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output CSV path, for example data/generated/orders_100k.csv.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible generated data.",
    )
    parser.add_argument(
        "--clean-columns",
        action="store_true",
        help="Use normalized snake_case column names instead of intentionally messy business-style names.",
    )
    parser.add_argument(
        "--no-issues",
        action="store_true",
        help="Disable intentional data quality issues.",
    )
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    df = generate_orders_dataframe(
        rows=args.rows,
        seed=args.seed,
        messy_column_names=not args.clean_columns,
        include_issues=not args.no_issues,
    )
    output_path = write_orders_csv(df, args.output)

    print("Synthetic order data generated")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Seed: {args.seed}")
    print(f"Output: {output_path}")
    print("Note: this is synthetic demo data, not real customer data.")


if __name__ == "__main__":
    main()
