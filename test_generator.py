import argparse
import csv
from datetime import datetime, timedelta
import random
from zoneinfo import ZoneInfo
from pathlib import Path
from uuid import uuid4
import logging
from tqdm.auto import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import StringIO
import os

logging.basicConfig(level=logging.INFO)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--num-sensors",
        type=int,
        default=10,
        help="Number of sensors to generate data for",
    )

    parser.add_argument(
        "--dir",
        type=str,
        default="records",
        help="Directory to save the generated data",
    )

    parser.add_argument(
        "--num-records",
        type=int,
        default=100,
        help="Number of records to generate for each sensor",
    )

    parser.add_argument(
        "--record-interval",
        type=float,
        default=1,
        help="Interval between records in seconds",
    )

    parser.add_argument(
        "--start-date",
        type=str,
        default="2021-01-01",
        help="Start date for the generated data (YYYY-MM-DD)",
    )

    parser.add_argument(
        "--timezone",
        type=str,
        default="Asia/Hong_Kong",
        help="Timezone for the generated data",
    )
    return parser.parse_args()


def generate_data(
    sensor_id: str,
    num_records: int,
    record_interval: int,
    start_date: datetime,
    base_dir: Path,
) -> None:
    with (base_dir / f"{sensor_id}.csv").open("w") as f:
        with StringIO() as buffer:
            writer = csv.DictWriter(
                buffer, fieldnames=["record_time", "sensor_id", "value"]
            )
            writer.writeheader()
            all_dates = [
                start_date + timedelta(seconds=i * record_interval)
                for i in range(num_records)
            ]

            all_random_values = [random.random() for _ in range(num_records)]

            writer.writerows(
                [
                    {
                        "record_time": date.isoformat(),
                        "sensor_id": sensor_id,
                        "value": random_value,
                    }
                    for date, random_value in zip(all_dates, all_random_values)
                ]
            )
            f.write(buffer.getvalue())


def main(
    num_sensors: int,
    num_records: int,
    record_interval: int,
    start_date_str: str,
    dir: str,
    timezone: str,
) -> None:
    logging.info("Generating data...")

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(
        tzinfo=ZoneInfo(timezone)
    )
    base_dir = Path(dir)
    base_dir.mkdir(exist_ok=True)
    futures = []
    with tqdm(total=num_sensors) as pbar:
        with ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as executor:
            for i in range(num_sensors):
                sensor_id = f"{uuid4().hex[:8]}_{i}"
                futures.append(
                    executor.submit(
                        generate_data,
                        sensor_id,
                        num_records,
                        record_interval,
                        start_date,
                        base_dir,
                    )
                )

            for _ in as_completed(futures):
                pbar.update(1)
    logging.info("Done")


if __name__ == "__main__":
    args = parse_args()
    main(
        args.num_sensors,
        args.num_records,
        args.record_interval,
        args.start_date,
        args.dir,
        args.timezone,
    )
