import pytest
from src.adapters.file_parse_iot_records.csv import CSVParseIOTRecordsClient
from pytest import FixtureRequest, LogCaptureFixture
from src.entities import IOTRecord
from pathlib import Path


def test_parse_single_dir_failed(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    caplog: LogCaptureFixture,
    tmp_path: Path,
):
    with caplog.at_level("ERROR"):
        iot_records = csv_parse_iot_records_client.parse(str(tmp_path))
        assert iot_records is None
        assert f"Failed to parse {tmp_path}" in caplog.text
        assert "File path must be a file!" in caplog.text


def test_parse_stream_dir_failed(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    caplog: LogCaptureFixture,
    tmp_path: Path,
):
    all_iot_records: list[IOTRecord] = []
    with caplog.at_level("ERROR"):
        for iot_record in csv_parse_iot_records_client.parse_stream(str(tmp_path)):
            assert isinstance(iot_record, IOTRecord)
            all_iot_records.append(iot_record)
        assert len(all_iot_records) == 0
        assert f"Failed to parse {tmp_path}" in caplog.text
        assert "File path must be a file!" in caplog.text


def test_parse_batch_other_format_failed(
    csv_parse_iot_records_client: CSVParseIOTRecordsClient,
    caplog: LogCaptureFixture,
    tmp_path: Path,
):
    tmp_paths = []
    for i in range(5):
        new_tmp_path = tmp_path / f"random_valid_tsv_file{i}"
        new_tmp_path.mkdir(parents=True, exist_ok=True)
        tmp_paths.append(new_tmp_path)

    tmp_paths_str = [str(tmp_path) for tmp_path in tmp_paths]

    with caplog.at_level("ERROR"):
        iot_records = csv_parse_iot_records_client.parse(tmp_paths_str)
        for random_file, iot_record in zip(tmp_paths_str, iot_records):
            assert iot_record is None
            assert f"Failed to parse {random_file}" in caplog.text
            assert "File path must be a file!" in caplog.text
