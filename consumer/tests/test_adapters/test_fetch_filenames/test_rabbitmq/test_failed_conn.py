import pytest
from .utils import random_csv_filenames
from src.adapters.fetch_filenames_stream.rabbitmq import (
    RabbitMQFetchFilenameStreamClient,
)
from src.deployments.script.config import RabbitMQConfig
import pika
from pytest import MonkeyPatch


@pytest.mark.smoke
def test_fetch_failed_conn(
    rabbitmq_fetch_filenames_stream_client: RabbitMQFetchFilenameStreamClient,
    monkeypatch: MonkeyPatch,
):
    def mocked_failed_conn(
        self,
        *args,
        **kwargs,
    ) -> None:
        raise Exception("Failed to connect")

    monkeypatch.setattr(pika.BlockingConnection, "__init__", mocked_failed_conn)

    monkeypatch.setattr(
        RabbitMQFetchFilenameStreamClient, "_reset_conn", mocked_failed_conn
    )

    with pytest.raises(Exception, match="^Failed to connect$"):
        next(rabbitmq_fetch_filenames_stream_client.fetch_stream())

    monkeypatch.undo()
    monkeypatch.undo()


@pytest.mark.smoke
def test_fetch_wrong_credentials(
    monkeypatch: MonkeyPatch,
):
    rabbitmq_fetch_filenames_stream_client = RabbitMQFetchFilenameStreamClient(
        host=RabbitMQConfig.HOST,
        port=RabbitMQConfig.PORT,
        credentials_service=lambda: ("wrong", "wrong"),
        queue=RabbitMQConfig.QUEUE,
        polling_timeout=RabbitMQConfig.POLLING_TIMEOUT,
    )

    def mocked_failed_conn(
        self,
        *args,
        **kwargs,
    ) -> None:
        raise Exception("Failed to connect")

    monkeypatch.setattr(
        RabbitMQFetchFilenameStreamClient, "_reset_conn", mocked_failed_conn
    )

    with pytest.raises(Exception, match="^Failed to connect$"):
        next(rabbitmq_fetch_filenames_stream_client.fetch_stream())

    monkeypatch.undo()


@pytest.mark.slow
@pytest.mark.smoke
def test_publish_single_wrong_host(
    monkeypatch: MonkeyPatch,
):
    rabbitmq_fetch_filenames_stream_client = RabbitMQFetchFilenameStreamClient(
        host="wrong",
        port=RabbitMQConfig.PORT,
        credentials_service=lambda: (RabbitMQConfig.USERNAME, RabbitMQConfig.PASSWORD),
        queue=RabbitMQConfig.QUEUE,
        polling_timeout=RabbitMQConfig.POLLING_TIMEOUT,
    )

    def mocked_failed_conn(
        self,
        *args,
        **kwargs,
    ) -> None:
        raise Exception("Failed to connect")

    monkeypatch.setattr(
        RabbitMQFetchFilenameStreamClient, "_reset_conn", mocked_failed_conn
    )

    with pytest.raises(Exception, match="^Failed to connect$") as e:
        next(rabbitmq_fetch_filenames_stream_client.fetch_stream())

    monkeypatch.undo()


@pytest.mark.slow
def test_fetch_failed_conn_reset_conn(
    rabbitmq_fetch_filenames_stream_no_wait_client: RabbitMQFetchFilenameStreamClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    monkeypatch: MonkeyPatch,
):
    conn, queue = raw_rabbitmq_pika_conn_config

    channel = conn.channel()

    channel.queue_declare(queue=queue, durable=True)

    first_published_filename = random_csv_filenames()[0]
    second_published_filename = random_csv_filenames()[1]

    channel.basic_publish(
        exchange="",
        routing_key=rabbitmq_fetch_filenames_stream_no_wait_client._queue,
        body=first_published_filename,
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )

    for i, (filename, receipt) in enumerate(
        rabbitmq_fetch_filenames_stream_no_wait_client.fetch_stream()
    ):
        if i == 0:
            assert rabbitmq_fetch_filenames_stream_no_wait_client._conn is not None
            conn = rabbitmq_fetch_filenames_stream_no_wait_client._conn

            assert filename == first_published_filename
            assert rabbitmq_fetch_filenames_stream_no_wait_client.ack(receipt)
            channel.basic_publish(
                exchange="",
                routing_key=rabbitmq_fetch_filenames_stream_no_wait_client._queue,
                body=second_published_filename,
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent
                ),
            )

            counter = 0

            def mock_failed_fetch(
                self,
                *args,
                **kwargs,
            ) -> None:
                nonlocal counter

                if counter == 0:
                    counter += 1
                    monkeypatch.undo()
                    raise Exception("Failed to fetch!")

            monkeypatch.setattr(pika.channel.Channel, "basic_get", mock_failed_fetch)
        if i == 1:
            assert filename == second_published_filename
            assert rabbitmq_fetch_filenames_stream_no_wait_client.ack(receipt)
            assert rabbitmq_fetch_filenames_stream_no_wait_client._conn is not None
            assert rabbitmq_fetch_filenames_stream_no_wait_client._conn != conn
