import pandas as pd

from dq_etl_starter.clean import clean_dataframe, standardize_country_names


def test_clean_dataframe_trims_and_deduplicates():
    df = pd.DataFrame({"name": [" Alice ", " Alice "], "country": ["usa", "usa"]})
    cleaned = clean_dataframe(df)
    assert len(cleaned) == 1
    assert cleaned.loc[0, "name"] == "Alice"
    assert cleaned.loc[0, "country"] == "United States"


def test_standardize_country_names():
    df = pd.DataFrame({"country": ["UK", " Singapore "]})
    cleaned = standardize_country_names(df)
    assert cleaned["country"].tolist() == ["United Kingdom", "Singapore"]
