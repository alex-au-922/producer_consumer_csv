import pytest
from src.adapters.file_parse_iot_records.csv import CSVParseIOTRecordsClient
from pytest import FixtureRequest, MonkeyPatch, LogCaptureFixture


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
def test_parse_stream_failed_open_file_raise(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_name: str,
    request: FixtureRequest,
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
):
    random_csv_file: str = request.getfixturevalue(fixture_name)

    def mock_open(*args, **kwargs):
        raise OSError("Failed to open file!")

    monkeypatch.setattr("builtins.open", mock_open)

    with caplog.at_level("ERROR"):
        with pytest.raises(Exception, match="^Failed to open file!$"):
            for _ in csv_parse_iot_records_client.parse_stream(random_csv_file):
                pass
        assert "Failed to open file!" in caplog.text
