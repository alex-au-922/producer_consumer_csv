from pytest import LogCaptureFixture
from src.adapters.upsert_iot_records.postgres import PostgresUpsertIOTRecordsClient
from .utils import random_iot_records, MockedPostgresConnection
import pytest


def test_close_conn_failed(
    postgres_upsert_iot_records_client: PostgresUpsertIOTRecordsClient,
    caplog: LogCaptureFixture,
):
    postgres_upsert_iot_records_client.upsert(random_iot_records()[0])

    assert postgres_upsert_iot_records_client._conn is not None

    postgres_upsert_iot_records_client._conn = MockedPostgresConnection()

    with caplog.at_level("ERROR"):
        assert not postgres_upsert_iot_records_client.close()
        assert "Failed to close!" in caplog.text
