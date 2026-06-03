from __future__ import annotations

import pandas as pd

from dq_etl_starter.normalize import standardize_text_values

COUNTRY_ALIASES = {
    "usa": "United States",
    "us": "United States",
    "u.s.": "United States",
    "united states": "United States",
    "united states of america": "United States",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "united kingdom": "United Kingdom",
    "england": "United Kingdom",
    "sg": "Singapore",
    "singapore": "Singapore",
}


def trim_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    return standardize_text_values(df)


def drop_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop=True)


def standardize_country_names(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    country_columns = [column for column in result.columns if column in {"country", "customer_country", "billing_country", "shipping_country"}]
    for column in country_columns:
        result[column] = result[column].map(
            lambda value: COUNTRY_ALIASES.get(value.strip().lower(), value.strip()) if isinstance(value, str) else value
        )
    return result


def clean_dataframe(df: pd.DataFrame, drop_duplicates: bool = True) -> pd.DataFrame:
    result = trim_whitespace(df)
    result = standardize_country_names(result)
    if drop_duplicates:
        result = drop_duplicate_rows(result)
    return result
