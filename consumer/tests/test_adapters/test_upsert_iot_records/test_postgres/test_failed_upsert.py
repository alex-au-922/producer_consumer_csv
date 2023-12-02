from __future__ import annotations
from datetime import datetime
from src.adapters.upsert_iot_records.postgres import PostgresUpsertIOTRecordsClient
from .utils import random_iot_records, MockedPostgresCursor, MockedPostgresConnection
import pytest
from src.entities import IOTRecord
import psycopg2
from pytest import MonkeyPatch


@pytest.mark.smoke
@pytest.mark.parametrize("iot_record", random_iot_records())
def test_upsert_single_failed(
    postgres_upsert_iot_records_client: PostgresUpsertIOTRecordsClient,
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
    iot_record: IOTRecord,
    monkeypatch: MonkeyPatch,
):
    monkeypatch.setattr(
        psycopg2, "connect", lambda *args, **kwargs: MockedPostgresConnection()
    )

    with pytest.raises(Exception) as e:
        assert not postgres_upsert_iot_records_client.upsert(iot_record)
        assert e.value == "Failed to execute!"

    with raw_postgres_psycopg2_conn_config.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                record_time,
                TRIM(sensor_id),
                value
                FROM records
                WHERE record_time = %s
                    AND sensor_id = %s
            """,
            (iot_record.record_time, iot_record.sensor_id),
        )

        assert cursor.fetchone() is None


@pytest.mark.smoke
@pytest.mark.parametrize(
    "iot_records",
    [random_iot_records() for _ in range(5)],
)
def test_upsert_batch_failed(
    postgres_upsert_iot_records_client: PostgresUpsertIOTRecordsClient,
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
    iot_records: list[IOTRecord],
    monkeypatch: MonkeyPatch,
):
    monkeypatch.setattr(
        psycopg2, "connect", lambda *args, **kwargs: MockedPostgresConnection()
    )

    with pytest.raises(Exception) as e:
        assert not any(postgres_upsert_iot_records_client.upsert(iot_records))
        assert e.value == "Failed to execute!"

    with raw_postgres_psycopg2_conn_config.cursor() as cursor:
        stmt = """
            SELECT
                record_time,
                TRIM(sensor_id),
                value
                FROM records
                WHERE (record_time, sensor_id) IN ({})
        """.format(
            ",".join(["%s"] * len(iot_records))
        )
        cursor.execute(
            stmt,
            [
                (iot_record.record_time, iot_record.sensor_id)
                for iot_record in iot_records
            ],
        )

        assert cursor.fetchone() is None


@pytest.mark.slow
@pytest.mark.parametrize(
    "iot_records",
    [random_iot_records() for _ in range(5)],
)
def test_upsert_batch_partial_failed(
    postgres_upsert_iot_records_client: PostgresUpsertIOTRecordsClient,
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
    iot_records: list[IOTRecord],
    monkeypatch: MonkeyPatch,
):
    new_postgres_upsert_iot_records_client = PostgresUpsertIOTRecordsClient(
        host=postgres_upsert_iot_records_client._host,
        port=postgres_upsert_iot_records_client._port,
        credentials_service=postgres_upsert_iot_records_client._credentials_service,
        database=postgres_upsert_iot_records_client._database,
        batch_upsert_size=1,
    )

    username, password = postgres_upsert_iot_records_client._credentials_service()

    valid_psycopg2_conn = psycopg2.connect(
        host=postgres_upsert_iot_records_client._host,
        port=postgres_upsert_iot_records_client._port,
        user=username,
        password=password,
        database=postgres_upsert_iot_records_client._database,
    )

    monkeypatch.setattr(
        psycopg2, "connect", lambda *args, **kwargs: MockedPostgresConnection()
    )

    counter = 0

    def mocked_partially_failed_upsert(
        self,
        *args,
        **kwargs,
    ) -> None:
        nonlocal counter
        counter += 1
        if counter == 3:
            raise Exception("Failed to execute!")
        else:
            with valid_psycopg2_conn.cursor() as cursor:
                try:
                    cursor.executemany(
                        *args,
                    )
                    valid_psycopg2_conn.commit()
                except Exception as e:
                    valid_psycopg2_conn.rollback()
                    raise e

    monkeypatch.setattr(
        MockedPostgresCursor, "executemany", mocked_partially_failed_upsert
    )

    with pytest.raises(Exception) as e:
        upsert_successes = new_postgres_upsert_iot_records_client.upsert(iot_records)

        assert not all(upsert_successes)
        assert any(upsert_successes)
        assert upsert_successes[2] == False
        assert e.value == "Failed to execute!"

    successful_records = [
        iot_record
        for iot_record, success in zip(iot_records, upsert_successes)
        if success
    ]

    with raw_postgres_psycopg2_conn_config.cursor() as cursor:
        stmt = """
            SELECT
                record_time,
                TRIM(sensor_id),
                value
                FROM records
                WHERE (record_time, sensor_id) IN ({})
        """.format(
            ",".join(["%s"] * len(successful_records))
        )
        cursor.execute(
            stmt,
            [
                (iot_record.record_time, iot_record.sensor_id)
                for iot_record in successful_records
            ],
        )

        record_time_sensor_id_map: dict[tuple[datetime, str], float] = {}

        for record_time, sensor_id, value in cursor.fetchall():
            record_time_sensor_id_map[(record_time, sensor_id)] = value

        for iot_record in successful_records:
            assert (
                pytest.approx(
                    record_time_sensor_id_map[
                        (iot_record.record_time, iot_record.sensor_id)
                    ]
                )
                == iot_record.value
            )
            record_time_sensor_id_map.pop(
                (iot_record.record_time, iot_record.sensor_id)
            )

        assert len(record_time_sensor_id_map) == 0
