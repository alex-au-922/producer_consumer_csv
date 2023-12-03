import pytest
from src.adapters.file_parse_iot_records.csv import CSVParseIOTRecordsClient
from pytest import FixtureRequest, MonkeyPatch, LogCaptureFixture
from src.entities import IOTRecord


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
def test_parse_single_failed_open_file(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_name: str,
    request: FixtureRequest,
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
):
    random_csv_file: str = request.getfixturevalue(fixture_name)

    def mock_open(*args, **kwargs):
        raise FileNotFoundError("Failed to open file!")

    monkeypatch.setattr("builtins.open", mock_open)

    with caplog.at_level("ERROR"):
        iot_records = csv_parse_iot_records_client.parse(random_csv_file)
        assert len(iot_records) == 0
        assert f"Failed to parse {random_csv_file}" in caplog.text
        assert "Failed to open file!" in caplog.text


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
def test_parse_stream_failed_open_file(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_name: str,
    request: FixtureRequest,
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
):
    random_csv_file: str = request.getfixturevalue(fixture_name)

    def mock_open(*args, **kwargs):
        raise FileNotFoundError("Failed to open file!")

    monkeypatch.setattr("builtins.open", mock_open)

    all_iot_records: list[IOTRecord] = []
    with caplog.at_level("ERROR"):
        for iot_record in csv_parse_iot_records_client.parse_stream(random_csv_file):
            assert isinstance(iot_record, IOTRecord)
            all_iot_records.append(iot_record)
        assert len(all_iot_records) == 0
        assert f"Failed to parse {random_csv_file}" in caplog.text
        assert "Failed to open file!" in caplog.text


@pytest.mark.smoke
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
def test_parse_batch_failed_open_file(
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
        raise FileNotFoundError("Failed to open file!")

    monkeypatch.setattr("builtins.open", mock_open)

    with caplog.at_level("ERROR"):
        iot_records = csv_parse_iot_records_client.parse(random_csv_files)
        for random_csv_file, iot_record in zip(random_csv_files, iot_records):
            assert len(iot_record) == 0
            assert f"Failed to parse {random_csv_file}" in caplog.text
            assert "Failed to open file!" in caplog.text
