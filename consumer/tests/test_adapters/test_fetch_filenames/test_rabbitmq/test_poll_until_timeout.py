import time
import pytest
from .utils import random_csv_filenames
from src.adapters.fetch_filenames.rabbitmq import RabbitMQFetchFilenamesClient
import pika
import pytest


@pytest.mark.smoke
@pytest.mark.parametrize("timeout", [0.5 * i for i in range(1, 5)])
def test_fetch_none_wait_timeout(
    rabbitmq_fetch_filenames_client: RabbitMQFetchFilenamesClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    timeout: int,
):
    new_rabbitmq_fetch_filenames_client = RabbitMQFetchFilenamesClient(
        host=rabbitmq_fetch_filenames_client._host,
        port=rabbitmq_fetch_filenames_client._port,
        credentials_service=rabbitmq_fetch_filenames_client._credentials_service,
        queue=rabbitmq_fetch_filenames_client._queue,
        polling_timeout=timeout,
    )

    conn, queue = raw_rabbitmq_pika_conn_config

    channel = conn.channel()

    channel.queue_declare(queue=queue, durable=True)

    filename = random_csv_filenames()[0]

    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=filename,
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )

    start_time = time.perf_counter()

    for fetched_filename in new_rabbitmq_fetch_filenames_client.fetch():
        assert fetched_filename == filename

    end_time = time.perf_counter()

    assert end_time - start_time >= timeout
