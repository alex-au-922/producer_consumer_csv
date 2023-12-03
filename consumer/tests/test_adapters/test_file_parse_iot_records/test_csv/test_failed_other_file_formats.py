import pytest
from src.adapters.file_parse_iot_records.csv import CSVParseIOTRecordsClient
from pytest import FixtureRequest, LogCaptureFixture
from src.entities import IOTRecord


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_name",
    [
        "random_valid_tsv_file",
        "random_invalid_datetime_and_value_tsv_file",
        "random_invalid_datetime_tsv_file",
        "random_invalid_value_tsv_file",
        "random_valid_ndjson_file",
        "random_invalid_datetime_and_value_ndjson_file",
        "random_invalid_datetime_ndjson_file",
        "random_invalid_value_ndjson_file",
    ]
    * 5,
)
def test_parse_single_other_format_failed(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_name: str,
    request: FixtureRequest,
    caplog: LogCaptureFixture,
):
    random_file: str = request.getfixturevalue(fixture_name)

    with caplog.at_level("ERROR"):
        iot_records = csv_parse_iot_records_client.parse(random_file)
        assert iot_records is None
        assert f"Failed to parse {random_file}" in caplog.text
        assert (
            f"File extension must be {csv_parse_iot_records_client._file_extension}"
            in caplog.text
        )


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_name",
    [
        "random_valid_tsv_file",
        "random_invalid_datetime_and_value_tsv_file",
        "random_invalid_datetime_tsv_file",
        "random_invalid_value_tsv_file",
        "random_valid_ndjson_file",
        "random_invalid_datetime_and_value_ndjson_file",
        "random_invalid_datetime_ndjson_file",
        "random_invalid_value_ndjson_file",
    ]
    * 5,
)
def test_parse_stream_other_format_failed(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_name: str,
    request: FixtureRequest,
    caplog: LogCaptureFixture,
):
    random_file: str = request.getfixturevalue(fixture_name)

    all_iot_records: list[IOTRecord] = []
    with caplog.at_level("ERROR"):
        for iot_record in csv_parse_iot_records_client.parse_stream(random_file):
            assert isinstance(iot_record, IOTRecord)
            all_iot_records.append(iot_record)
        assert len(all_iot_records) == 0
        assert f"Failed to parse {random_file}" in caplog.text
        assert (
            f"File extension must be {csv_parse_iot_records_client._file_extension}"
            in caplog.text
        )


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_names",
    [
        tuple(
            [
                "random_valid_tsv_file",
                "random_invalid_datetime_and_value_tsv_file",
                "random_invalid_datetime_tsv_file",
                "random_invalid_value_tsv_file",
                "random_valid_ndjson_file",
                "random_invalid_datetime_and_value_ndjson_file",
                "random_invalid_datetime_ndjson_file",
                "random_invalid_value_ndjson_file",
            ]
        )
        for _ in range(5)
    ],
)
def test_parse_batch_other_format_failed(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_names: tuple[str, ...],
    request: FixtureRequest,
    caplog: LogCaptureFixture,
):
    random_files: list[str] = [
        request.getfixturevalue(fixture_name) for fixture_name in fixture_names
    ]

    with caplog.at_level("ERROR"):
        iot_records = csv_parse_iot_records_client.parse(random_files)
        for random_file, iot_record in zip(random_files, iot_records):
            assert iot_record is None
            assert f"Failed to parse {random_file}" in caplog.text
            assert (
                f"File extension must be {csv_parse_iot_records_client._file_extension}"
                in caplog.text
            )
