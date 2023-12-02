import pytest
from .utils import random_csv_filenames
from src.adapters.fetch_filenames.rabbitmq import RabbitMQFetchFilenamesClient
import pika
import pytest


@pytest.mark.smoke
@pytest.mark.parametrize("filename", random_csv_filenames())
def test_fetch_single_success(
    rabbitmq_fetch_filenames_no_wait_client: RabbitMQFetchFilenamesClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filename: str,
):
    conn, queue = raw_rabbitmq_pika_conn_config

    channel = conn.channel()

    channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=rabbitmq_fetch_filenames_no_wait_client._queue,
        body=filename,
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )

    for fetched_filename in rabbitmq_fetch_filenames_no_wait_client.fetch():
        assert fetched_filename == filename


@pytest.mark.smoke
@pytest.mark.parametrize(
    "filenames",
    [random_csv_filenames() for _ in range(5)],
)
def test_publish_batch_success(
    rabbitmq_fetch_filenames_no_wait_client: RabbitMQFetchFilenamesClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filenames: list[str],
):
    conn, queue = raw_rabbitmq_pika_conn_config

    channel = conn.channel()

    channel.queue_declare(queue=queue, durable=True)

    for filename in filenames:
        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=filename,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
        )

    all_filenames = []
    for filename in rabbitmq_fetch_filenames_no_wait_client.fetch():
        all_filenames.append(filename)

    assert sorted(all_filenames) == sorted(filenames)
