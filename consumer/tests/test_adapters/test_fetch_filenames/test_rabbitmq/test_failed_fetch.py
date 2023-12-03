import pytest
from .utils import random_csv_filenames
from src.adapters.fetch_filenames_stream.rabbitmq import (
    RabbitMQFetchFilenameStreamClient,
)
import pika
import pytest
from pytest import LogCaptureFixture, MonkeyPatch


@pytest.mark.smoke
@pytest.mark.parametrize("filename", random_csv_filenames())
def test_fetch_single_exception_resilience(
    rabbitmq_fetch_filenames_stream_no_wait_client: RabbitMQFetchFilenameStreamClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filename: str,
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    conn, queue = raw_rabbitmq_pika_conn_config

    channel = conn.channel()
    channel.queue_declare(
        queue=queue,
        durable=True,
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
    with caplog.at_level("ERROR"):
        for (
            fetched_filename,
            receipt,
        ) in rabbitmq_fetch_filenames_stream_no_wait_client.fetch_stream():
            assert fetched_filename == filename
            assert rabbitmq_fetch_filenames_stream_no_wait_client.ack(receipt)
            assert "Failed to fetch!" in caplog.text


@pytest.mark.smoke
@pytest.mark.parametrize(
    "filenames",
    [random_csv_filenames() for _ in range(5)],
)
def test_fetch_batch_exception_resilience(
    rabbitmq_fetch_filenames_stream_no_wait_client: RabbitMQFetchFilenameStreamClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filenames: list[str],
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    conn, queue = raw_rabbitmq_pika_conn_config

    channel = conn.channel()
    channel.queue_declare(
        queue=queue,
        durable=True,
    )

    for filename in filenames:
        channel.basic_publish(
            exchange="",
            routing_key=rabbitmq_fetch_filenames_stream_no_wait_client._queue,
            body=filename,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
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

    all_filenames = []

    with caplog.at_level("ERROR"):
        for (
            fetched_filename,
            receipt,
        ) in rabbitmq_fetch_filenames_stream_no_wait_client.fetch_stream():
            all_filenames.append(fetched_filename)
            assert rabbitmq_fetch_filenames_stream_no_wait_client.ack(receipt)
            assert "Failed to fetch!" in caplog.text

    assert sorted(all_filenames) == sorted(filenames)


@pytest.mark.parametrize("filename", random_csv_filenames())
def test_fetch_single_ack_exception_resilience(
    rabbitmq_fetch_filenames_stream_client: RabbitMQFetchFilenameStreamClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filename: str,
    monkeypatch: MonkeyPatch,
):
    new_rabbitmq_fetch_filenames_stream_client = RabbitMQFetchFilenameStreamClient(
        host=rabbitmq_fetch_filenames_stream_client._host,
        port=rabbitmq_fetch_filenames_stream_client._port,
        credentials_service=rabbitmq_fetch_filenames_stream_client._credentials_service,
        queue=rabbitmq_fetch_filenames_stream_client._queue,
        polling_timeout=1,
    )

    conn, queue = raw_rabbitmq_pika_conn_config

    channel = conn.channel()
    channel.queue_declare(
        queue=queue,
        durable=True,
    )

    channel.basic_publish(
        exchange="",
        routing_key=rabbitmq_fetch_filenames_stream_client._queue,
        body=filename,
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )

    counter = 0

    def mock_failed_ack(
        self,
        *args,
        **kwargs,
    ) -> None:
        nonlocal counter

        if counter == 0:
            counter += 1
            monkeypatch.undo()
            raise Exception("Failed to ack!")

    monkeypatch.setattr(pika.channel.Channel, "basic_ack", mock_failed_ack)

    for (
        fetched_filename,
        receipt,
    ) in new_rabbitmq_fetch_filenames_stream_client.fetch_stream():
        monkeypatch.undo()
        assert fetched_filename == filename
        assert new_rabbitmq_fetch_filenames_stream_client.ack(receipt)
