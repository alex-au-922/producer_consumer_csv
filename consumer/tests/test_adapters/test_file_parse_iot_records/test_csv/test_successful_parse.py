import pytest
from src.adapters.file_parse_iot_records.csv import CSVParseIOTRecordsClient
from src.entities import IOTRecord
from pytest import FixtureRequest


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_name",
    ["random_valid_csv_file"] * 5,
)
def test_parse_single_successful(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_name: str,
    request: FixtureRequest,
):
    random_valid_csv_file: str = request.getfixturevalue(fixture_name)
    iot_records = csv_parse_iot_records_client.parse(random_valid_csv_file)
    assert len(iot_records) > 0


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_names",
    [tuple(["random_valid_csv_file" for _ in range(10)]) for _ in range(5)],
)
def test_parse_batch_successful(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_names: tuple[str, ...],
    request: FixtureRequest,
):
    random_valid_csv_files: list[str] = [
        request.getfixturevalue(fixture_name) for fixture_name in fixture_names
    ]
    iot_records = csv_parse_iot_records_client.parse(random_valid_csv_files)

    for iot_record in iot_records:
        assert len(iot_record) > 0


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_name",
    ["random_valid_csv_file"] * 5,
)
def test_parse_stream_successful(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    fixture_name: str,
    request: FixtureRequest,
):
    random_valid_csv_file: str = request.getfixturevalue(fixture_name)
    all_iot_records: list[IOTRecord] = []
    for iot_record in csv_parse_iot_records_client.parse_stream(random_valid_csv_file):
        assert isinstance(iot_record, IOTRecord)
        all_iot_records.append(iot_record)

    iot_records = csv_parse_iot_records_client.parse(random_valid_csv_file)

    assert sorted(
        all_iot_records, key=lambda iot_record: iot_record.record_time
    ) == sorted(iot_records, key=lambda iot_record: iot_record.record_time)
