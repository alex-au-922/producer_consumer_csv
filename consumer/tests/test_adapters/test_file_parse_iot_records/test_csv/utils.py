from decimal import Decimal
import random
import string
import csv
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import zoneinfo
import random
import json


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
        rows.append((random_datetime.isoformat(), random_sensor_id, str(random_value)))
    return rows


def random_invalid_datetime_rows() -> list[tuple[str, ...]]:
    rows = []
    all_datetime_formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M%z",
    ]
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
        random_datetime_format = random.choice(all_datetime_formats)
        rows.append(
            (
                random_datetime.strftime(random_datetime_format),
                random_sensor_id,
                str(random_value),
            )
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
            (
                random_datetime.isoformat(),
                random_sensor_id,
                random_value,
            )
        )
    return rows


def random_invalid_datetime_and_value_rows() -> list[tuple[str, ...]]:
    rows = []
    all_datetime_formats = [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M%z",
        "%Y-%m-%d %H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M%z",
    ]
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
        random_datetime_format = random.choice(all_datetime_formats)
        rows.append(
            (
                random_datetime.strftime(random_datetime_format),
                random_sensor_id,
                str(random_value),
            )
        )
    return rows


def random_csv_file(base_dir: Path, rows: list[tuple[str, ...]]) -> str:
    filename = "".join(random.choices(string.ascii_letters, k=10)) + ".csv"
    filepath = base_dir.joinpath(filename)
    with open(filepath, "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerows(rows)
    return str(filepath)


def random_tsv_file(base_dir: Path, rows: list[tuple[str, ...]]) -> str:
    filename = "".join(random.choices(string.ascii_letters, k=10)) + ".tsv"
    filepath = base_dir.joinpath(filename)
    with open(filepath, "w") as csvfile:
        writer = csv.writer(csvfile, delimiter="\t")
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
