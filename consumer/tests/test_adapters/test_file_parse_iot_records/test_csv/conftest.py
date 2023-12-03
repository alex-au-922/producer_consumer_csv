from .utils import (
    random_csv_file,
    random_tsv_file,
    random_ndjson_file,
    random_invalid_datetime_rows,
    random_invalid_datetime_and_value_rows,
    random_invalid_value_rows,
    random_valid_format_rows,
)
import pytest
from pytest import TempdirFactory
from pathlib import Path
from src.adapters.file_parse_iot_records.csv import CSVParseIOTRecordsClient
from src.deployments.script.config import CSVParserConfig


@pytest.fixture(scope="session")
def setup_tempdir(tmpdir_factory: TempdirFactory) -> Path:
    return Path(tmpdir_factory.mktemp("artifact"))


@pytest.fixture(scope="function")
def random_valid_csv_file(setup_tempdir: Path) -> Path:
    return random_csv_file(setup_tempdir, random_valid_format_rows())


@pytest.fixture(scope="function")
def random_invalid_datetime_and_value_csv_file(setup_tempdir: Path) -> Path:
    return random_csv_file(setup_tempdir, random_invalid_datetime_and_value_rows())


@pytest.fixture(scope="function")
def random_invalid_datetime_csv_file(setup_tempdir: Path) -> Path:
    return random_csv_file(setup_tempdir, random_invalid_datetime_rows())


@pytest.fixture(scope="function")
def random_invalid_value_csv_file(setup_tempdir: Path) -> Path:
    return random_csv_file(setup_tempdir, random_invalid_value_rows())


@pytest.fixture(scope="function")
def random_valid_tsv_file(setup_tempdir: Path) -> Path:
    return random_tsv_file(setup_tempdir, random_valid_format_rows())


@pytest.fixture(scope="function")
def random_invalid_datetime_and_value_tsv_file(setup_tempdir: Path) -> Path:
    return random_tsv_file(setup_tempdir, random_invalid_datetime_and_value_rows())


@pytest.fixture(scope="function")
def random_invalid_datetime_tsv_file(setup_tempdir: Path) -> Path:
    return random_tsv_file(setup_tempdir, random_invalid_datetime_rows())


@pytest.fixture(scope="function")
def random_invalid_value_tsv_file(setup_tempdir: Path) -> Path:
    return random_tsv_file(setup_tempdir, random_invalid_value_rows())


@pytest.fixture(scope="function")
def random_valid_ndjson_file(setup_tempdir: Path) -> Path:
    return random_ndjson_file(setup_tempdir, random_valid_format_rows())


@pytest.fixture(scope="function")
def random_invalid_datetime_and_value_ndjson_file(setup_tempdir: Path) -> Path:
    return random_ndjson_file(setup_tempdir, random_invalid_datetime_and_value_rows())


@pytest.fixture(scope="function")
def random_invalid_datetime_ndjson_file(setup_tempdir: Path) -> Path:
    return random_ndjson_file(setup_tempdir, random_invalid_datetime_rows())


@pytest.fixture(scope="function")
def random_invalid_value_ndjson_file(setup_tempdir: Path) -> Path:
    return random_ndjson_file(setup_tempdir, random_invalid_value_rows())


@pytest.fixture(scope="function")
def csv_parse_iot_records_client() -> CSVParseIOTRecordsClient:
    return CSVParseIOTRecordsClient(
        recognized_datetime_formats=CSVParserConfig.RECOGNIZED_DATETIME_FORMATS,
        delimiter=CSVParserConfig.DELIMITER,
        file_extension=CSVParserConfig.FILE_EXTENSION,
    )
