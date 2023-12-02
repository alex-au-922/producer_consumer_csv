from src.adapters.upsert_iot_records.postgres import PostgresUpsertIOTRecordsClient
from .utils import random_iot_records


def test_close_conn_successful(
    postgres_upsert_iot_records_client: PostgresUpsertIOTRecordsClient,
):
    postgres_upsert_iot_records_client.upsert(random_iot_records()[0])
    assert postgres_upsert_iot_records_client._conn is not None
    assert postgres_upsert_iot_records_client.close()


def test_none_conn_close_successful(
    postgres_upsert_iot_records_client: PostgresUpsertIOTRecordsClient,
):
    assert postgres_upsert_iot_records_client.close()
