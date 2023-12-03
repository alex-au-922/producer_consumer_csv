from src.deployments.script.config import RabbitMQConfig, PostgresConfig
import pika
import pytest
import psycopg2
from pytest import TempdirFactory
from pathlib import Path
from .utils import (
    random_csv_file,
    random_tsv_file,
    random_ndjson_file,
    random_invalid_datetime_rows,
    random_invalid_datetime_and_value_rows,
    random_invalid_value_rows,
    random_valid_format_rows,
)


@pytest.fixture(scope="session")
def setup_tempdir(tmpdir_factory: TempdirFactory) -> Path:
    return Path(tmpdir_factory.mktemp("artifact"))


@pytest.fixture(scope="session")
def raw_postgres_psycopg2_conn_config() -> psycopg2.extensions.connection:
    with psycopg2.connect(
        host=PostgresConfig.HOST,
        port=PostgresConfig.PORT,
        user=PostgresConfig.USERNAME,
        password=PostgresConfig.PASSWORD,
        database=PostgresConfig.DATABASE,
    ) as conn:
        yield conn


@pytest.fixture(scope="session")
def raw_rabbitmq_pika_conn_config() -> tuple[pika.BaseConnection, str]:
    pika_conn = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RabbitMQConfig.HOST,
            port=RabbitMQConfig.PORT,
            credentials=pika.PlainCredentials(
                RabbitMQConfig.USERNAME, RabbitMQConfig.PASSWORD
            ),
        )
    )
    return pika_conn, RabbitMQConfig.QUEUE


@pytest.fixture(scope="session", autouse=True)
def init_postgres_tables(
    raw_postgres_psycopg2_conn_config: psycopg2.extensions.connection,
) -> None:
    with raw_postgres_psycopg2_conn_config.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                record_time TIMESTAMPTZ NOT NULL,
                sensor_id TEXT NOT NULL,
                value DOUBLE PRECISION NOT NULL,
                PRIMARY KEY(record_time, sensor_id)
            );

            CREATE INDEX IF NOT EXISTS idx_records_record_time ON records USING BRIN (record_time);
            CREATE INDEX IF NOT EXISTS idx_records_sensor_id ON records USING HASH (sensor_id);
            """
        )
        raw_postgres_psycopg2_conn_config.commit()


@pytest.fixture(scope="function", autouse=True)
def setup_teardown_rabbitmq_queue(
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
) -> None:
    pika_conn, queue = raw_rabbitmq_pika_conn_config

    channel = pika_conn.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.queue_purge(queue=queue)
    yield
    channel.queue_purge(queue=queue)


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


@pytest.fixture(scope="session")
def setup_tempdir(tmpdir_factory: TempdirFactory) -> Path:
    return Path(tmpdir_factory.mktemp("artifact"))


@pytest.fixture(scope="function")
def random_valid_csv_file(setup_tempdir: Path) -> Path:
    return random_csv_file(setup_tempdir, random_valid_format_rows())


@pytest.fixture(scope="function")
def random_invalid_datetime_and_value_csv_file(setup_tempdir: Path) -> Path:
    return random_csv_file(setup_tempdir, random_invalid_datetime_and_value_rows())


@pytest.fixture(scope="function")
def random_invalid_datetime_csv_file(setup_tempdir: Path) -> Path:
    return random_csv_file(setup_tempdir, random_invalid_datetime_rows())


@pytest.fixture(scope="function")
def random_invalid_value_csv_file(setup_tempdir: Path) -> Path:
    return random_csv_file(setup_tempdir, random_invalid_value_rows())


@pytest.fixture(scope="function")
def random_valid_tsv_file(setup_tempdir: Path) -> Path:
    return random_tsv_file(setup_tempdir, random_valid_format_rows())


@pytest.fixture(scope="function")
def random_invalid_datetime_and_value_tsv_file(setup_tempdir: Path) -> Path:
    return random_tsv_file(setup_tempdir, random_invalid_datetime_and_value_rows())


@pytest.fixture(scope="function")
def random_invalid_datetime_tsv_file(setup_tempdir: Path) -> Path:
    return random_tsv_file(setup_tempdir, random_invalid_datetime_rows())


@pytest.fixture(scope="function")
def random_invalid_value_tsv_file(setup_tempdir: Path) -> Path:
    return random_tsv_file(setup_tempdir, random_invalid_value_rows())


@pytest.fixture(scope="function")
def random_valid_ndjson_file(setup_tempdir: Path) -> Path:
    return random_ndjson_file(setup_tempdir, random_valid_format_rows())


@pytest.fixture(scope="function")
def random_invalid_datetime_and_value_ndjson_file(setup_tempdir: Path) -> Path:
    return random_ndjson_file(setup_tempdir, random_invalid_datetime_and_value_rows())


@pytest.fixture(scope="function")
def random_invalid_datetime_ndjson_file(setup_tempdir: Path) -> Path:
    return random_ndjson_file(setup_tempdir, random_invalid_datetime_rows())


@pytest.fixture(scope="function")
def random_invalid_value_ndjson_file(setup_tempdir: Path) -> Path:
    return random_ndjson_file(setup_tempdir, random_invalid_value_rows())
