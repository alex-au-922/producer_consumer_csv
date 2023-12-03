import pytest
from src.adapters.upsert_iot_records.postgres import PostgresUpsertIOTRecordsClient
from src.deployments.script.config import PostgresConfig
from src.entities import IOTRecord
import psycopg2
from .utils import random_iot_records, MockedPostgresConnection
from pytest import MonkeyPatch, LogCaptureFixture


@pytest.mark.smoke
@pytest.mark.parametrize("iot_record", random_iot_records())
def test_upsert_single_failed_conn(
    postgres_upsert_iot_records_client: PostgresUpsertIOTRecordsClient,
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
    iot_record: IOTRecord,
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    def mocked_failed_conn(
        *args,
        **kwargs,
    ) -> None:
        raise Exception("Failed to connect")

    monkeypatch.setattr(psycopg2, "connect", mocked_failed_conn)

    with caplog.at_level("ERROR"):
        assert not postgres_upsert_iot_records_client.upsert(iot_record)
        assert "Failed to connect" in caplog.text

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
def test_upsert_batch_failed_conn(
    postgres_upsert_iot_records_client: PostgresUpsertIOTRecordsClient,
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
    iot_records: list[IOTRecord],
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    def mocked_failed_conn(
        *args,
        **kwargs,
    ) -> None:
        raise Exception("Failed to connect")

    monkeypatch.setattr(psycopg2, "connect", mocked_failed_conn)

    with caplog.at_level("ERROR"):
        assert not any(postgres_upsert_iot_records_client.upsert(iot_records))
        assert "Failed to connect" in caplog.text

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


@pytest.mark.smoke
@pytest.mark.parametrize("iot_record", random_iot_records())
def test_upsert_single_wrong_credentials(
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
    iot_record: IOTRecord,
    caplog: LogCaptureFixture,
):
    postgres_upsert_iot_records_client = PostgresUpsertIOTRecordsClient(
        host=PostgresConfig.HOST,
        port=PostgresConfig.PORT,
        credentials_service=lambda: ("wrong", "wrong"),
        database=PostgresConfig.DATABASE,
        batch_upsert_size=1,
    )

    with caplog.at_level("ERROR"):
        assert not postgres_upsert_iot_records_client.upsert(iot_record)
        assert "ERROR" in caplog.text

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


@pytest.mark.slow
@pytest.mark.smoke
@pytest.mark.parametrize("iot_record", random_iot_records())
def test_upsert_single_wrong_host(
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
    iot_record: IOTRecord,
    caplog: LogCaptureFixture,
):
    postgres_upsert_iot_records_client = PostgresUpsertIOTRecordsClient(
        host="wrong",
        port=PostgresConfig.PORT,
        credentials_service=lambda: (PostgresConfig.USERNAME, PostgresConfig.PASSWORD),
        database=PostgresConfig.DATABASE,
        batch_upsert_size=1,
    )

    with caplog.at_level("ERROR"):
        assert not postgres_upsert_iot_records_client.upsert(iot_record)
        assert "ERROR" in caplog.text

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


@pytest.mark.slow
@pytest.mark.parametrize("iot_record", random_iot_records())
def test_upsert_single_failed_conn_reset_conn(
    postgres_upsert_iot_records_client: PostgresUpsertIOTRecordsClient,
    iot_record: IOTRecord,
    monkeypatch: MonkeyPatch,
):
    assert postgres_upsert_iot_records_client._conn is None
    assert postgres_upsert_iot_records_client.upsert(iot_record)
    conn = postgres_upsert_iot_records_client._conn
    assert conn is not None

    def mock_failed_conn(
        self,
        *args,
        **kwargs,
    ) -> None:
        raise Exception("Failed to connect")

    monkeypatch.setattr(PostgresUpsertIOTRecordsClient, "_get_conn", mock_failed_conn)

    assert not postgres_upsert_iot_records_client.upsert(iot_record)

    monkeypatch.undo()

    assert postgres_upsert_iot_records_client._conn is None

    assert postgres_upsert_iot_records_client.upsert(iot_record)
    assert postgres_upsert_iot_records_client._conn != conn


@pytest.mark.slow
@pytest.mark.parametrize(
    "iot_records",
    [random_iot_records() for _ in range(5)],
)
def test_upsert_batch_failed_conn_reset_conn(
    postgres_upsert_iot_records_client: PostgresUpsertIOTRecordsClient,
    iot_records: list[IOTRecord],
    monkeypatch: MonkeyPatch,
):
    assert postgres_upsert_iot_records_client._conn is None
    assert all(postgres_upsert_iot_records_client.upsert(iot_records))
    conn = postgres_upsert_iot_records_client._conn
    assert conn is not None

    def mock_failed_conn(
        self,
        *args,
        **kwargs,
    ) -> None:
        raise Exception("Failed to connect")

    monkeypatch.setattr(PostgresUpsertIOTRecordsClient, "_get_conn", mock_failed_conn)

    assert not any(postgres_upsert_iot_records_client.upsert(iot_records))

    monkeypatch.undo()

    assert postgres_upsert_iot_records_client._conn is None

    assert all(postgres_upsert_iot_records_client.upsert(iot_records))
    assert postgres_upsert_iot_records_client._conn != conn
