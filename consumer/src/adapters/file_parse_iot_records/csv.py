from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from decimal import Decimal
from typing import Iterator, Optional, overload, Sequence
from typing_extensions import override
from entities import IOTRecord
from usecases import FileParseIOTRecordsClient
import csv
import logging


class CSVParseIOTRecordsClient(FileParseIOTRecordsClient):
    def __init__(
        self,
        recognized_datetime_formats: Sequence[str],
        delimiter: str = ",",
    ) -> None:
        self._delimiter = delimiter
        self._recognized_datetime_formats = recognized_datetime_formats

    @overload
    def parse(self, filename: str) -> list[IOTRecord]:
        ...

    @overload
    def parse(self, filename: Sequence[str]) -> list[list[IOTRecord]]:
        ...

    @override
    def parse(
        self, filename: str | Sequence[str]
    ) -> list[IOTRecord] | list[list[IOTRecord]]:
        if isinstance(filename, str):
            return self._parse_single(filename)
        return self._parse_batch(filename)

    @override
    def parse_stream(self, filename: str) -> Iterator[IOTRecord]:
        try:
            with open(filename) as csvfile:
                reader = csv.reader(csvfile, delimiter=self._delimiter)
                yield from self._parse_iter(reader)
        except Exception as e:
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
        except ValueError:
            return None

    def _parse_iter(self, reader: Iterator[list[str]]) -> Iterator[IOTRecord]:
        iot_records: list[IOTRecord] = []
        for row in reader:
            try:
                parsed_datetime = self._parse_datetime(row[0])
                if parsed_datetime is None:
                    raise ValueError(f"Unrecognized datetime format: {row[0]}")

                parsed_value = self._parse_value(row[2])
                if parsed_value is None:
                    raise ValueError(f"Unrecognized value format: {row[2]}")

                yield IOTRecord(
                    datetime=parsed_datetime,
                    sensor_id=str(row[1]),
                    value=parsed_value,
                )
            except Exception as e:
                logging.exception(e)
        return iot_records

    def _parse_single(self, filename: str) -> list[IOTRecord]:
        try:
            with open(filename) as csvfile:
                reader = csv.reader(csvfile, delimiter=self._delimiter)
                return list(self._parse_iter(reader))
        except Exception as e:
            logging.exception(e)
            return []

    def _parse_batch(self, filenames: Sequence[str]) -> list[list[IOTRecord]]:
        with ThreadPoolExecutor() as executor:
            return list(executor.map(self._parse_single, filenames))

    @override
    def close(self) -> bool:
        return True
