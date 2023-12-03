from __future__ import annotations
import string
from decimal import Decimal
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import zoneinfo
from src.entities.iot_record import IOTRecord


def random_iot_records() -> list[IOTRecord]:
    all_iot_records = []
    all_available_timezones = list(zoneinfo.available_timezones())
    for _ in range(5):
        random_timezone = random.choice(all_available_timezones)
        random_time_delta = timedelta(
            hours=random.randint(0, 24),
            minutes=random.randint(0, 60),
            seconds=random.randint(0, 60),
        )
        all_iot_records.append(
            IOTRecord(
                record_time=datetime.now(tz=ZoneInfo(random_timezone))
                - random_time_delta,
                sensor_id="".join(random.choices(string.ascii_letters, k=10)),
                value=Decimal(random.random() * 100),
            )
        )
    return all_iot_records


class MockedPostgresCursor:
    def __enter__(self, *args, **kwargs) -> MockedPostgresCursor:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        pass

    def execute(self, *args, **kwargs) -> None:
        raise Exception("Failed to execute!")

    def executemany(self, *args, **kwargs) -> None:
        raise Exception("Failed to execute!")


class MockedPostgresConnection:
    def cursor(self) -> MockedPostgresCursor:
        return MockedPostgresCursor()

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def __enter__(self, *args, **kwargs) -> MockedPostgresConnection:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        pass

    @property
    def closed(self) -> bool:
        return False

    def close(self) -> None:
        raise Exception("Failed to close!")
