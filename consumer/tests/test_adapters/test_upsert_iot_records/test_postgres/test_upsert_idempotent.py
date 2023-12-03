from datetime import datetime
from src.adapters.upsert_iot_records.postgres import PostgresUpsertIOTRecordsClient
from .utils import random_iot_records
import pytest
from src.entities import IOTRecord
import psycopg2


@pytest.mark.smoke
@pytest.mark.parametrize("iot_record", random_iot_records())
def test_upsert_single_iot_record_idempotent(
    postgres_upsert_iot_records_client: PostgresUpsertIOTRecordsClient,
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
    iot_record: IOTRecord,
):
    assert postgres_upsert_iot_records_client.upsert(iot_record)
    assert postgres_upsert_iot_records_client.upsert(iot_record)

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

        results = cursor.fetchall()
        for record_time, sensor_id, value in results:
            assert record_time == iot_record.record_time
            assert sensor_id == iot_record.sensor_id
            assert pytest.approx(value) == iot_record.value

        assert len(results) == 1


@pytest.mark.smoke
@pytest.mark.parametrize("iot_records", [random_iot_records() for _ in range(5)])
def test_upsert_batch_iot_records_idempotent(
    postgres_upsert_iot_records_client: PostgresUpsertIOTRecordsClient,
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
    iot_records: list[IOTRecord],
):
    assert all(postgres_upsert_iot_records_client.upsert(iot_records))
    assert all(postgres_upsert_iot_records_client.upsert(iot_records))

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

        record_time_sensor_id_map: dict[tuple[datetime, str], float] = {}

        for record_time, sensor_id, value in cursor.fetchall():
            if (record_time, sensor_id) in record_time_sensor_id_map:
                assert False
            record_time_sensor_id_map[(record_time, sensor_id)] = value

        for iot_record in iot_records:
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
