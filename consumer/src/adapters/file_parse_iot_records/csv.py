from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation
from typing import Iterator, Optional, overload, Sequence
from typing_extensions import override
from ...entities import IOTRecord
from ...usecases import FileParseIOTRecordsClient
import csv
import logging
from pathlib import Path


class CSVParseIOTRecordsClient(FileParseIOTRecordsClient):
    def __init__(
        self,
        recognized_datetime_formats: Sequence[str],
        delimiter: str = ",",
        file_extension: str = ".csv",
    ) -> None:
        self._delimiter = delimiter
        self._recognized_datetime_formats = recognized_datetime_formats
        self._file_extension = file_extension

    @overload
    def parse(self, filename: str) -> Optional[list[IOTRecord]]:
        ...

    @overload
    def parse(self, filename: Sequence[str]) -> list[Optional[list[IOTRecord]]]:
        ...

    @override
    def parse(
        self, filename: str | Sequence[str]
    ) -> Optional[list[IOTRecord]] | list[Optional[list[IOTRecord]]]:
        if isinstance(filename, str):
            return self._parse_single(filename)
        return self._parse_batch(filename)

    def _basic_file_check(self, filename: str) -> bool:
        if not Path(filename).exists():
            raise ValueError("File path must exist!")
        if not Path(filename).is_file():
            raise ValueError("File path must be a file!")
        if not filename.endswith(self._file_extension):
            raise ValueError(f"File extension must be {self._file_extension}")

    @override
    def parse_stream(self, filename: str) -> Iterator[IOTRecord]:
        try:
            self._basic_file_check(filename)
            with open(filename) as csvfile:
                reader = csv.reader(csvfile, delimiter=self._delimiter, strict=True)
                yield from self._parse_iter(reader)
        except OSError as e:
            logging.exception(e)
            logging.error(f"Failed to read stream from {filename}!")
            raise e
        except Exception as e:
            logging.error(f"Failed to parse {filename}")
            logging.exception(e)

    def _parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        for datetime_format in self._recognized_datetime_formats:
            try:
                return datetime.strptime(datetime_str, datetime_format)
            except ValueError:
                pass
        return None

    def _parse_value(self, value_str: str) -> Optional[Decimal]:
        try:
            return Decimal(value_str)
        except InvalidOperation:
            return None

    def _parse_iter(self, reader: Iterator[list[str]]) -> Iterator[IOTRecord]:
        iot_records: list[IOTRecord] = []
        for row in reader:
            parsed_datetime = self._parse_datetime(row[0])
            if parsed_datetime is None:
                logging.warning(f"Unrecognized datetime format: {row[0]}")

            parsed_value = self._parse_value(row[2])
            if parsed_value is None:
                logging.warning(f"Unrecognized value format: {row[2]}")

            if parsed_datetime is None or parsed_value is None:
                continue

            yield IOTRecord(
                record_time=parsed_datetime,
                sensor_id=str(row[1]),
                value=parsed_value,
            )
        return iot_records

    def _parse_single(self, filename: str) -> Optional[list[IOTRecord]]:
        try:
            self._basic_file_check(filename)
            with open(filename) as csvfile:
                reader = csv.reader(csvfile, delimiter=self._delimiter)
                return list(self._parse_iter(reader))
        except Exception as e:
            logging.exception(e)
            logging.error(f"Failed to parse {filename}")
            return None

    def _parse_batch(self, filenames: Sequence[str]) -> list[list[IOTRecord]]:
        with ThreadPoolExecutor() as executor:
            return list(executor.map(self._parse_single, filenames))

    @override
    def close(self) -> bool:
        return True
