from src.adapters.publish_filenames.rabbitmq import RabbitMQPublishFilenamesClient
import pika
import pytest


@pytest.fixture(scope="session")
def rabbitmq_config() -> dict:
    return {
        "host": "localhost",
        "port": 5672,
        "credentials_service": lambda: ("guest", "guest"),
        "queue": "filenames",
    }


@pytest.fixture(scope="session")
def rabbitmq_publish_filenames_client(
    rabbitmq_config: dict,
) -> RabbitMQPublishFilenamesClient:
    return RabbitMQPublishFilenamesClient(**rabbitmq_config)


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="function")
def clean_rabbitmq_queue(
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
) -> None:
    pika_conn, queue = raw_rabbitmq_pika_conn_config

    channel = pika_conn.channel()
    channel.queue_purge(queue=queue)


class TestSuccessfulPublish:
    @pytest.mark.smoke
    def test_publish_single(
        self,
        rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
        raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
        random_filenames: list[str],
    ):
        for filename in random_filenames:
            assert rabbitmq_publish_filenames_client.publish(filename)

        pika_conn, queue = raw_rabbitmq_pika_conn_config

        channel = pika_conn.channel()
        for filename in random_filenames:
            method_frame, _, body = channel.basic_get(queue=queue)
            assert method_frame is not None
            assert body.decode() == filename
            channel.basic_ack(method_frame.delivery_tag)

    @pytest.mark.smoke
    def test_publish_batch(
        self,
        rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
        raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
        random_filenames: list[str],
    ):
        assert all(rabbitmq_publish_filenames_client.publish(random_filenames))

        pika_conn, queue = raw_rabbitmq_pika_conn_config

        channel = pika_conn.channel()
        for filename in random_filenames:
            method_frame, _, body = channel.basic_get(queue=queue)
            assert method_frame is not None
            assert body.decode() == filename
            channel.basic_ack(method_frame.delivery_tag)
