from src.deployments.script.main import main
from src.deployments.script.config import RabbitMQConfig
import pytest
from pytest import MonkeyPatch, LogCaptureFixture, FixtureRequest
from src.adapters.upsert_iot_records.postgres import PostgresUpsertIOTRecordsClient
import pika
import psycopg2
import csv
from datetime import datetime
from decimal import Decimal


@pytest.mark.parametrize(
    "fixture_name",
    ["random_valid_csv_file"] * 5,
)
def test_main_flow_single_upsert_record_failed_resilience(
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

    counter = 0

    def mock_upsert(*args, **kwargs):
        nonlocal counter
        counter += 1
        if counter == 1:
            monkeypatch.undo()
            raise Exception("Failed to upsert!")

    monkeypatch.setattr(
        "src.deployments.script.main._upsert_iot_records_buffer", mock_upsert
    )

    with caplog.at_level("INFO"):
        main()
        assert "Failed to upsert!" in caplog.text
        assert f"Failed to upsert {random_csv_file}!" in caplog.text
        assert f"Successfully upserted {random_csv_file}!" in caplog.text

    with open(random_csv_file, "r") as f:
        reader = csv.reader(f)
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
def test_main_flow_single_upsert_step_failed_resilience(
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

    counter = 0

    def mock_upsert(self, records) -> list[bool]:
        nonlocal counter
        counter += 1
        if counter == 1:
            monkeypatch.undo()
            return [False] * len(records)

    monkeypatch.setattr(PostgresUpsertIOTRecordsClient, "_upsert_batch", mock_upsert)

    with caplog.at_level("INFO"):
        main()
        assert "Failed to upsert all records!" in caplog.text
        assert f"Failed to upsert {random_csv_file}!" in caplog.text
        assert f"Successfully upserted {random_csv_file}!" in caplog.text

    with open(random_csv_file, "r") as f:
        reader = csv.reader(f)
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
