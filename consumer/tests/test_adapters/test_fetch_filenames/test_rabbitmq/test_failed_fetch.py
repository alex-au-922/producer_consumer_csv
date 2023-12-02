import pytest
from .utils import random_csv_filenames
from src.adapters.fetch_filenames.rabbitmq import RabbitMQFetchFilenamesClient
import pika
import pytest
from pytest import LogCaptureFixture, MonkeyPatch


@pytest.mark.smoke
@pytest.mark.parametrize("filename", random_csv_filenames())
def test_fetch_single_exception_resilience(
    rabbitmq_fetch_filenames_no_wait_client: RabbitMQFetchFilenamesClient,
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
        for fetched_filename in rabbitmq_fetch_filenames_no_wait_client.fetch():
            assert fetched_filename == filename
            assert "Failed to fetch!" in caplog.text


@pytest.mark.smoke
@pytest.mark.parametrize(
    "filenames",
    [random_csv_filenames() for _ in range(5)],
)
def test_fetch_batch_exception_resilience(
    rabbitmq_fetch_filenames_no_wait_client: RabbitMQFetchFilenamesClient,
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
            routing_key=rabbitmq_fetch_filenames_no_wait_client._queue,
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
        for fetched_filename in rabbitmq_fetch_filenames_no_wait_client.fetch():
            all_filenames.append(fetched_filename)
            assert "Failed to fetch!" in caplog.text

    assert sorted(all_filenames) == sorted(filenames)
