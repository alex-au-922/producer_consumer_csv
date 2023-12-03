import pytest
from .utils import random_csv_filenames
from src.adapters.fetch_filenames_stream.rabbitmq import (
    RabbitMQFetchFilenameStreamClient,
)
import pika
from pytest import MonkeyPatch


@pytest.mark.parametrize("filename", random_csv_filenames())
def test_fetch_single_ack_failed(
    rabbitmq_fetch_filenames_stream_no_wait_client: RabbitMQFetchFilenameStreamClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filename: str,
    monkeypatch: MonkeyPatch,
):
    conn, queue = raw_rabbitmq_pika_conn_config

    channel = conn.channel()

    channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=rabbitmq_fetch_filenames_stream_no_wait_client._queue,
        body=filename,
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )

    for (
        fetched_filename,
        receipt,
    ) in rabbitmq_fetch_filenames_stream_no_wait_client.fetch_stream():
        assert fetched_filename == filename

    def mock_ack(self, *args, **kwargs):
        raise Exception("Failed to ack!")

    monkeypatch.setattr(pika.channel.Channel, "basic_ack", mock_ack)

    assert not rabbitmq_fetch_filenames_stream_no_wait_client.ack(receipt)
