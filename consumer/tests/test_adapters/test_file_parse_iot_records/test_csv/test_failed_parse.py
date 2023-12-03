import pytest
from src.adapters.file_parse_iot_records.csv import CSVParseIOTRecordsClient
from src.entities import IOTRecord
from pytest import FixtureRequest, LogCaptureFixture


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_name",
    ["random_invalid_value_csv_file"] * 5,
)
def test_parse_single_decimal_failed_ignore_row(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_name: str,
    request: FixtureRequest,
    caplog: LogCaptureFixture,
):
    random_invalid_value_csv_file: str = request.getfixturevalue(fixture_name)

    with caplog.at_level("WARNING"):
        iot_records = csv_parse_iot_records_client.parse(random_invalid_value_csv_file)
        assert len(iot_records) == 0
        assert "Unrecognized value format:" in caplog.text
        assert "Unrecognized datetime format:" not in caplog.text


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_name",
    ["random_invalid_datetime_csv_file"] * 5,
)
def test_parse_single_datetime_failed_ignore_row(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_name: str,
    request: FixtureRequest,
    caplog: LogCaptureFixture,
):
    random_invalid_datetime_csv_file: str = request.getfixturevalue(fixture_name)

    with caplog.at_level("WARNING"):
        iot_records = csv_parse_iot_records_client.parse(
            random_invalid_datetime_csv_file
        )
        assert len(iot_records) == 0
        assert "Unrecognized datetime format:" in caplog.text
        assert "Unrecognized value format:" not in caplog.text


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_name",
    ["random_invalid_datetime_and_value_csv_file"] * 5,
)
def test_parse_single_datetime_and_value_failed_ignore_row(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_name: str,
    request: FixtureRequest,
    caplog: LogCaptureFixture,
):
    random_invalid_datetime_and_value_csv_file: str = request.getfixturevalue(
        fixture_name
    )

    with caplog.at_level("WARNING"):
        iot_records = csv_parse_iot_records_client.parse(
            random_invalid_datetime_and_value_csv_file
        )
        assert len(iot_records) == 0
        assert "Unrecognized datetime format:" in caplog.text
        assert "Unrecognized value format:" in caplog.text


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_name",
    ["random_invalid_value_csv_file"] * 5,
)
def test_parse_stream_decimal_failed_ignore_row(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_name: str,
    request: FixtureRequest,
    caplog: LogCaptureFixture,
):
    random_invalid_value_csv_file: str = request.getfixturevalue(fixture_name)

    all_iot_records: list[IOTRecord] = []
    with caplog.at_level("WARNING"):
        for iot_records in csv_parse_iot_records_client.parse_stream(
            random_invalid_value_csv_file
        ):
            all_iot_records.append(iot_records)
        assert len(all_iot_records) == 0
        assert "Unrecognized value format:" in caplog.text
        assert "Unrecognized datetime format:" not in caplog.text


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_name",
    ["random_invalid_datetime_csv_file"] * 5,
)
def test_parse_stream_datetime_failed_ignore_row(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_name: str,
    request: FixtureRequest,
    caplog: LogCaptureFixture,
):
    random_invalid_datetime_csv_file: str = request.getfixturevalue(fixture_name)

    all_iot_records: list[IOTRecord] = []
    with caplog.at_level("WARNING"):
        for iot_records in csv_parse_iot_records_client.parse_stream(
            random_invalid_datetime_csv_file
        ):
            all_iot_records.append(iot_records)
        assert len(all_iot_records) == 0
        assert "Unrecognized datetime format:" in caplog.text
        assert "Unrecognized value format:" not in caplog.text


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_name",
    ["random_invalid_datetime_and_value_csv_file"] * 5,
)
def test_parse_stream_datetime_and_value_failed_ignore_row(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_name: str,
    request: FixtureRequest,
    caplog: LogCaptureFixture,
):
    random_invalid_datetime_and_value_csv_file: str = request.getfixturevalue(
        fixture_name
    )

    all_iot_records: list[IOTRecord] = []
    with caplog.at_level("WARNING"):
        for iot_records in csv_parse_iot_records_client.parse_stream(
            random_invalid_datetime_and_value_csv_file
        ):
            all_iot_records.append(iot_records)
        assert len(all_iot_records) == 0
        assert "Unrecognized datetime format:" in caplog.text
        assert "Unrecognized value format:" in caplog.text


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_names",
    [tuple(["random_invalid_value_csv_file"] * 5) for _ in range(5)],
)
def test_parse_batch_decimal_failed_ignore_row(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_names: tuple[str, ...],
    request: FixtureRequest,
    caplog: LogCaptureFixture,
):
    random_invalid_value_csv_files: list[str] = [
        request.getfixturevalue(fixture_name) for fixture_name in fixture_names
    ]

    with caplog.at_level("WARNING"):
        iot_records = csv_parse_iot_records_client.parse(random_invalid_value_csv_files)

        for iot_record in iot_records:
            assert len(iot_record) == 0

        assert "Unrecognized value format:" in caplog.text
        assert "Unrecognized datetime format:" not in caplog.text


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_names",
    [tuple(["random_invalid_datetime_csv_file"] * 5) for _ in range(5)],
)
def test_parse_batch_datetime_failed_ignore_row(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_names: tuple[str, ...],
    request: FixtureRequest,
    caplog: LogCaptureFixture,
):
    random_invalid_datetime_csv_files: list[str] = [
        request.getfixturevalue(fixture_name) for fixture_name in fixture_names
    ]

    with caplog.at_level("WARNING"):
        iot_records = csv_parse_iot_records_client.parse(
            random_invalid_datetime_csv_files
        )

        for iot_record in iot_records:
            assert len(iot_record) == 0

        assert "Unrecognized datetime format:" in caplog.text
        assert "Unrecognized value format:" not in caplog.text


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_names",
    [tuple(["random_invalid_datetime_and_value_csv_file"] * 5) for _ in range(5)],
)
def test_parse_batch_datetime_and_value_failed_ignore_row(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_names: tuple[str, ...],
    request: FixtureRequest,
    caplog: LogCaptureFixture,
):
    random_invalid_datetime_and_value_csv_files: list[str] = [
        request.getfixturevalue(fixture_name) for fixture_name in fixture_names
    ]

    with caplog.at_level("WARNING"):
        iot_records = csv_parse_iot_records_client.parse(
            random_invalid_datetime_and_value_csv_files
        )

        for iot_record in iot_records:
            assert len(iot_record) == 0

        assert "Unrecognized datetime format:" in caplog.text
        assert "Unrecognized value format:" in caplog.text
