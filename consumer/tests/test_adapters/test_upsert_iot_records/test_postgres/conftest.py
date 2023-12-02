from src.adapters.upsert_iot_records.postgres import PostgresUpsertIOTRecordsClient
from src.deployments.scripts.config import PostgresConfig
import psycopg2
import pytest


@pytest.fixture(scope="session", autouse=True)
def init_postgres_tables() -> None:
    with psycopg2.connect(
        host=PostgresConfig.HOST,
        port=PostgresConfig.PORT,
        user=PostgresConfig.USERNAME,
        password=PostgresConfig.PASSWORD,
        database=PostgresConfig.DATABASE,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS records (
                    record_time TIMESTAMPTZ NOT NULL,
                    sensor_id CHAR(64) NOT NULL,
                    value DOUBLE PRECISION NOT NULL,
                    PRIMARY KEY(record_time, sensor_id)
                );

                CREATE INDEX IF NOT EXISTS idx_records_record_time ON records USING BTREE (record_time);
                CREATE INDEX IF NOT EXISTS idx_records_sensor_id ON records USING BTREE (sensor_id);
                """
            )
            conn.commit()


@pytest.fixture(scope="function")
def postgres_upsert_iot_records_client() -> PostgresUpsertIOTRecordsClient:
    return PostgresUpsertIOTRecordsClient(
        host=PostgresConfig.HOST,
        port=PostgresConfig.PORT,
        credentials_service=lambda: (PostgresConfig.USERNAME, PostgresConfig.PASSWORD),
        database=PostgresConfig.DATABASE,
        batch_upsert_size=PostgresConfig.BATCH_UPSERT_SIZE,
    )


@pytest.fixture(scope="function")
def raw_postgres_psycopg2_conn_config() -> psycopg2.extensions.connection:
    with psycopg2.connect(
        host=PostgresConfig.HOST,
        port=PostgresConfig.PORT,
        user=PostgresConfig.USERNAME,
        password=PostgresConfig.PASSWORD,
        database=PostgresConfig.DATABASE,
    ) as conn:
        yield conn


@pytest.fixture(scope="function", autouse=True)
def setup_teardown_postgres_tables(
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
) -> None:
    with raw_postgres_psycopg2_conn_config.cursor() as cursor:
        try:
            cursor.execute(
                """
                TRUNCATE TABLE records;
                """
            )
            raw_postgres_psycopg2_conn_config.commit()
            yield
        except Exception as e:
            raw_postgres_psycopg2_conn_config.rollback()
            raise e
        finally:
            cursor.execute(
                """
                TRUNCATE TABLE records;
                """
            )
            raw_postgres_psycopg2_conn_config.commit()
