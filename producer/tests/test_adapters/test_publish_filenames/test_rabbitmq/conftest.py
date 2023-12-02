from src.adapters.publish_filenames.rabbitmq import RabbitMQPublishFilenamesClient
import pika
import pytest
from pytest import MonkeyPatch


@pytest.fixture(scope="session")
def rabbitmq_config() -> dict:
    return {
        "host": "localhost",
        "port": 5672,
        "credentials_service": lambda: ("rabbitmq", "rabbitmq"),
        "queue": "filenames",
    }


@pytest.fixture(scope="function")
def rabbitmq_publish_filenames_client(
    rabbitmq_config: dict,
) -> RabbitMQPublishFilenamesClient:
    return RabbitMQPublishFilenamesClient(**rabbitmq_config)


@pytest.fixture(scope="function")
def raw_rabbitmq_pika_conn_config(
    rabbitmq_config: dict,
) -> tuple[pika.BaseConnection, str]:
    pika_conn = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_config["host"],
            port=rabbitmq_config["port"],
            credentials=pika.PlainCredentials(
                *rabbitmq_config["credentials_service"]()
            ),
        )
    )
    return pika_conn, rabbitmq_config["queue"]


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


@pytest.fixture(scope="function")
def patch_failed_publish(monkeypatch: MonkeyPatch) -> None:
    def mocked_failed_basic_publish(
        self,
        *args,
        **kwargs,
    ) -> None:
        raise Exception("Failed to publish")

    monkeypatch.setattr(
        pika.channel.Channel, "basic_publish", mocked_failed_basic_publish
    )
