from pytest import MonkeyPatch, LogCaptureFixture
import pika
from src.adapters.fetch_filenames_stream.rabbitmq import (
    RabbitMQFetchFilenameStreamClient,
)
from .utils import random_csv_filenames


def test_close_conn_failed(
    rabbitmq_fetch_filenames_stream_no_wait_client: RabbitMQFetchFilenameStreamClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    conn, _ = raw_rabbitmq_pika_conn_config

    channel = conn.channel()

    channel.queue_declare(
        queue=rabbitmq_fetch_filenames_stream_no_wait_client._queue, durable=True
    )

    channel.basic_publish(
        exchange="",
        routing_key=rabbitmq_fetch_filenames_stream_no_wait_client._queue,
        body=random_csv_filenames()[0],
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )

    for (
        filename,
        receipt,
    ) in rabbitmq_fetch_filenames_stream_no_wait_client.fetch_stream():
        assert filename is not None
        assert rabbitmq_fetch_filenames_stream_no_wait_client.ack(receipt)

    assert rabbitmq_fetch_filenames_stream_no_wait_client._conn is not None

    def mock_failed_close(
        self,
        *args,
        **kwargs,
    ) -> None:
        raise Exception("Failed to close!")

    monkeypatch.setattr(pika.BlockingConnection, "close", mock_failed_close)

    with caplog.at_level("ERROR"):
        assert not rabbitmq_fetch_filenames_stream_no_wait_client.close()
        assert "Failed to close!" in caplog.text
