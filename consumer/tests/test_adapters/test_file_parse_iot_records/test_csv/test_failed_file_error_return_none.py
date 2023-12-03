import pytest
from src.adapters.file_parse_iot_records.csv import CSVParseIOTRecordsClient
from pytest import FixtureRequest, MonkeyPatch, LogCaptureFixture


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
def test_parse_single_failed_open_file_return_none(
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
        assert csv_parse_iot_records_client.parse(random_csv_file) is None
        assert "Failed to open file!" in caplog.text


@pytest.mark.parametrize(
    "fixture_names",
    [
        tuple(
            [
                "random_valid_csv_file",
                "random_invalid_datetime_and_value_csv_file",
                "random_invalid_datetime_csv_file",
                "random_invalid_value_csv_file",
            ]
        )
        for _ in range(5)
    ],
)
def test_parse_batch_failed_open_file_return_none(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_names: tuple[str, ...],
    request: FixtureRequest,
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
):
    random_csv_files: list[str] = [
        request.getfixturevalue(fixture_name) for fixture_name in fixture_names
    ]

    def mock_open(*args, **kwargs):
        raise OSError("Failed to open file!")

    monkeypatch.setattr("builtins.open", mock_open)

    with caplog.at_level("ERROR"):
        for parsed_record in csv_parse_iot_records_client.parse(random_csv_files):
            assert parsed_record is None
        assert "Failed to open file!" in caplog.text
