import random
import string
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import zoneinfo
import random
import json
from decimal import Decimal
import csv


def random_valid_format_rows() -> list[tuple[str, ...]]:
    rows = []
    for _ in range(10):
        random_timezone = random.choice(list(zoneinfo.available_timezones()))
        random_time_delta = timedelta(
            hours=random.randint(0, 24),
            minutes=random.randint(0, 60),
            seconds=random.randint(0, 60),
        )
        random_datetime = datetime.now(tz=ZoneInfo(random_timezone)) - random_time_delta
        random_sensor_id = "".join(random.choices(string.ascii_letters, k=10))
        random_value = Decimal(random.random() * 100)
        rows.append(
            {
                "record_time": random_datetime.isoformat(timespec="milliseconds"),
                "sensor_id": random_sensor_id,
                "value": str(random_value),
            }
        )
    return rows


def random_invalid_datetime_rows() -> list[tuple[str, ...]]:
    rows = []
    for _ in range(10):
        random_sensor_id = "".join(random.choices(string.ascii_letters, k=10))
        random_value = Decimal(random.random() * 100)
        rows.append(
            {
                "record_time": "".join(random.choices(string.ascii_letters, k=10)),
                "sensor_id": random_sensor_id,
                "value": str(random_value),
            }
        )
    return rows


def random_invalid_value_rows() -> list[tuple[str, ...]]:
    rows = []
    for _ in range(10):
        random_timezone = random.choice(list(zoneinfo.available_timezones()))
        random_time_delta = timedelta(
            hours=random.randint(0, 24),
            minutes=random.randint(0, 60),
            seconds=random.randint(0, 60),
        )
        random_datetime = datetime.now(tz=ZoneInfo(random_timezone)) - random_time_delta
        random_sensor_id = "".join(random.choices(string.ascii_letters, k=10))
        random_value = "".join(random.choices(string.ascii_letters, k=10))
        rows.append(
            {
                "record_time": random_datetime.isoformat(timespec="milliseconds"),
                "sensor_id": random_sensor_id,
                "value": random_value,
            }
        )
    return rows


def random_invalid_datetime_and_value_rows() -> list[tuple[str, ...]]:
    rows = []
    for _ in range(10):
        random_sensor_id = "".join(random.choices(string.ascii_letters, k=10))
        random_value = "".join(random.choices(string.ascii_letters, k=10))
        rows.append(
            {
                "record_time": "".join(random.choices(string.ascii_letters, k=10)),
                "sensor_id": random_sensor_id,
                "value": random_value,
            }
        )
    return rows


def random_csv_file(base_dir: Path, rows: list[tuple[str, ...]]) -> str:
    filename = "".join(random.choices(string.ascii_letters, k=10)) + ".csv"
    filepath = base_dir.joinpath(filename)
    with open(filepath, "w") as csvfile:
        writer = csv.DictWriter(
            csvfile, delimiter=",", fieldnames=["record_time", "sensor_id", "value"]
        )
        writer.writeheader()
        writer.writerows(rows)
    return str(filepath)


def random_tsv_file(base_dir: Path, rows: list[tuple[str, ...]]) -> str:
    filename = "".join(random.choices(string.ascii_letters, k=10)) + ".tsv"
    filepath = base_dir.joinpath(filename)
    with open(filepath, "w") as csvfile:
        writer = csv.DictWriter(
            csvfile, delimiter="\t", fieldnames=["record_time", "sensor_id", "value"]
        )
        writer.writeheader()
        writer.writerows(rows)
    return str(filepath)


def random_ndjson_file(base_dir: Path, rows: list[tuple[str, ...]]) -> str:
    filename = "".join(random.choices(string.ascii_letters, k=10)) + ".tsv"
    filepath = base_dir.joinpath(filename)
    with open(filepath, "w") as csvfile:
        for row in rows:
            json.dump(row, csvfile)
            csvfile.write("\n")
    return str(filepath)
