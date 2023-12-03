from src.deployments.script.main import main
from src.deployments.script.config import RabbitMQConfig, PostgresConfig
import pytest
from pytest import MonkeyPatch, LogCaptureFixture, FixtureRequest
import pika
import psycopg2
import csv
from datetime import datetime
from decimal import Decimal


@pytest.mark.parametrize(
    "fixture_name",
    ["random_valid_csv_file"] * 5,
)
def test_main_flow_single_no_failed_files(
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    fixture_name: str,
    request: FixtureRequest,
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    random_csv_file: str = request.getfixturevalue(fixture_name)

    conn, queue = raw_rabbitmq_pika_conn_config
    channel = conn.channel()
    channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=random_csv_file,
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )

    monkeypatch.setattr(RabbitMQConfig, "POLLING_TIMEOUT", 1)

    with caplog.at_level("INFO"):
        main()
        assert f"Successfully upserted {random_csv_file}!" in caplog.text

    with open(random_csv_file, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            record_time, sensor_id, value = row

            record_time_dt = datetime.fromisoformat(record_time)
            value_dec = Decimal(value)

            with raw_postgres_psycopg2_conn_config.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT record_time, sensor_id, value
                    FROM records
                    WHERE record_time = %s AND sensor_id = %s;
                    """,
                    (record_time_dt, sensor_id),
                )

                (
                    fetched_record_time,
                    fetched_sensor_id,
                    fetched_value,
                ) = cursor.fetchone()

                assert fetched_record_time == record_time_dt
                assert fetched_sensor_id == sensor_id
                assert pytest.approx(value_dec) == fetched_value

    method_frame, header_frame, body = channel.basic_get(queue=queue)
    assert method_frame is None
    assert header_frame is None
    assert body is None


@pytest.mark.parametrize(
    "fixture_names",
    [tuple(["random_valid_csv_file"] * 5) for _ in range(5)],
)
def test_main_flow_batch_no_failed_files(
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    fixture_names: tuple[str, ...],
    request: FixtureRequest,
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    random_csv_files: list[str] = [
        request.getfixturevalue(fixture_name) for fixture_name in fixture_names
    ]

    conn, queue = raw_rabbitmq_pika_conn_config
    channel = conn.channel()
    channel.queue_declare(queue=queue, durable=True)

    for random_csv_file in random_csv_files:
        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=random_csv_file,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
        )

    monkeypatch.setattr(RabbitMQConfig, "POLLING_TIMEOUT", 1)

    with caplog.at_level("INFO"):
        main()
        assert f"Successfully upserted {random_csv_file}!" in caplog.text

    for random_csv_file in random_csv_files:
        with open(random_csv_file, "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                record_time, sensor_id, value = row

                record_time_dt = datetime.fromisoformat(record_time)
                value_dec = Decimal(value)

                with raw_postgres_psycopg2_conn_config.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT record_time, sensor_id, value
                        FROM records
                        WHERE record_time = %s AND sensor_id = %s;
                        """,
                        (record_time_dt, sensor_id),
                    )

                    (
                        fetched_record_time,
                        fetched_sensor_id,
                        fetched_value,
                    ) = cursor.fetchone()

                    assert fetched_record_time == record_time_dt
                    assert fetched_sensor_id == sensor_id
                    assert pytest.approx(value_dec) == fetched_value

    method_frame, header_frame, body = channel.basic_get(queue=queue)
    assert method_frame is None
    assert header_frame is None
    assert body is None


@pytest.mark.parametrize(
    "fixture_name",
    ["random_valid_csv_file"] * 5,
)
def test_main_flow_single_in_batch_no_failed_files(
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    fixture_name: str,
    request: FixtureRequest,
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    random_csv_file: str = request.getfixturevalue(fixture_name)

    conn, queue = raw_rabbitmq_pika_conn_config
    channel = conn.channel()
    channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=random_csv_file,
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )

    monkeypatch.setattr(RabbitMQConfig, "POLLING_TIMEOUT", 1)

    monkeypatch.setattr(PostgresConfig, "BATCH_UPSERT_SIZE", 3)

    with caplog.at_level("INFO"):
        main()
        assert f"Successfully upserted {random_csv_file}!" in caplog.text

    with open(random_csv_file, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            record_time, sensor_id, value = row

            record_time_dt = datetime.fromisoformat(record_time)
            value_dec = Decimal(value)

            with raw_postgres_psycopg2_conn_config.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT record_time, sensor_id, value
                    FROM records
                    WHERE record_time = %s AND sensor_id = %s;
                    """,
                    (record_time_dt, sensor_id),
                )

                result = cursor.fetchone()

                fetched_record_time, fetched_sensor_id, fetched_value = result

                assert fetched_record_time == record_time_dt
                assert fetched_sensor_id == sensor_id
                assert pytest.approx(value_dec) == fetched_value

    method_frame, header_frame, body = channel.basic_get(queue=queue)
    assert method_frame is None
    assert header_frame is None
    assert body is None


@pytest.mark.parametrize(
    "fixture_names",
    [tuple(["random_valid_csv_file"] * 5) for _ in range(5)],
)
def test_main_flow_batch_in_batch_no_failed_files(
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    fixture_names: tuple[str, ...],
    request: FixtureRequest,
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    random_csv_files: list[str] = [
        request.getfixturevalue(fixture_name) for fixture_name in fixture_names
    ]

    conn, queue = raw_rabbitmq_pika_conn_config
    channel = conn.channel()
    channel.queue_declare(queue=queue, durable=True)

    for random_csv_file in random_csv_files:
        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=random_csv_file,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
        )

    monkeypatch.setattr(RabbitMQConfig, "POLLING_TIMEOUT", 1)

    monkeypatch.setattr(PostgresConfig, "BATCH_UPSERT_SIZE", 2)

    with caplog.at_level("INFO"):
        main()
        assert f"Successfully upserted {random_csv_file}!" in caplog.text

    for random_csv_file in random_csv_files:
        with open(random_csv_file, "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                record_time, sensor_id, value = row

                record_time_dt = datetime.fromisoformat(record_time)
                value_dec = Decimal(value)

                with raw_postgres_psycopg2_conn_config.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT record_time, sensor_id, value
                        FROM records
                        WHERE record_time = %s AND sensor_id = %s;
                        """,
                        (record_time_dt, sensor_id),
                    )

                    (
                        fetched_record_time,
                        fetched_sensor_id,
                        fetched_value,
                    ) = cursor.fetchone()

                    assert fetched_record_time == record_time_dt
                    assert fetched_sensor_id == sensor_id
                    assert pytest.approx(value_dec) == fetched_value

    method_frame, header_frame, body = channel.basic_get(queue=queue)
    assert method_frame is None
    assert header_frame is None
    assert body is None
