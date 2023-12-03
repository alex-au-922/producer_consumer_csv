import pytest
from src.adapters.file_parse_iot_records.csv import CSVParseIOTRecordsClient
from pytest import FixtureRequest


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_name",
    [
        "random_valid_csv_file",
        "random_invalid_datetime_and_value_csv_file",
        "random_invalid_datetime_csv_file",
        "random_invalid_value_csv_file",
    ]
    * 5,
)
def test_close_always_successful(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_name: str,
    request: FixtureRequest,
):
    random_valid_csv_file: str = request.getfixturevalue(fixture_name)

    csv_parse_iot_records_client.parse(random_valid_csv_file)

    assert csv_parse_iot_records_client.close()
