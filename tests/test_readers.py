from dq_etl_starter.mock_api import mock_api_response_to_dataframe
from dq_etl_starter.readers import read_csv_file, read_excel_file, read_json_file


def test_read_csv_file_normalizes_columns():
    df = read_csv_file("data/input/messy_customers.csv")
    assert "customer_id" in df.columns
    assert "full_name" in df.columns


def test_read_excel_file():
    df = read_excel_file("data/input/messy_orders.xlsx")
    assert "order_id" in df.columns
    assert len(df) >= 3


def test_read_nested_json_file():
    df = read_json_file("data/input/nested_customers.json", records_path="data.customers")
    assert "profile_email" in df.columns
    assert "address_country" in df.columns


def test_mock_api_response_to_dataframe():
    df = mock_api_response_to_dataframe("data/input/mock_api_orders.json", records_path="data.orders")
    assert "customer_email" in df.columns
    assert "shipping_country" in df.columns
