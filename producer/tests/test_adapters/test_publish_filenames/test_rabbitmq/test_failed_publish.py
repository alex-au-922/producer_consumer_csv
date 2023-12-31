import pytest
from .utils import random_filenames
from src.adapters.publish_filenames.rabbitmq import RabbitMQPublishFilenamesClient
import pika
import pytest
from pytest import LogCaptureFixture, MonkeyPatch


@pytest.mark.smoke
@pytest.mark.usefixtures("patch_failed_publish")
@pytest.mark.parametrize("filename", random_filenames())
def test_publish_single_failed(
    rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filename: str,
    caplog: LogCaptureFixture,
):
    with caplog.at_level("ERROR"):
        assert not rabbitmq_publish_filenames_client.publish(filename)
        assert "Failed to publish" in caplog.text

    pika_conn, queue = raw_rabbitmq_pika_conn_config

    channel = pika_conn.channel()
    method_frame, _, body = channel.basic_get(queue=queue)
    assert method_frame is None
    assert body is None


@pytest.mark.smoke
@pytest.mark.usefixtures("patch_failed_publish")
@pytest.mark.parametrize(
    "filenames",
    [random_filenames() for _ in range(5)],
)
def test_publish_batch_failed(
    rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filenames: list[str],
    caplog: LogCaptureFixture,
):
    with caplog.at_level("ERROR"):
        assert not any(rabbitmq_publish_filenames_client.publish(filenames))
        assert "Failed to publish" in caplog.text

    pika_conn, queue = raw_rabbitmq_pika_conn_config

    channel = pika_conn.channel()
    for _ in filenames:
        method_frame, _, body = channel.basic_get(queue=queue)
        assert method_frame is None
        assert body is None


@pytest.mark.parametrize(
    "filenames",
    [random_filenames() for _ in range(5)],
)
def test_publish_batch_partial_failed(
    rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filenames: list[str],
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    counter = 0

    def mocked_partially_failed_basic_publish(
        self,
        *args,
        **kwargs,
    ) -> None:
        nonlocal counter
        counter += 1
        if counter == 3:
            raise Exception("Failed to publish")
        else:
            with rabbitmq_publish_filenames_client._get_amqp_conn() as connection:
                channel = connection.channel()
                channel.queue_declare(
                    queue=rabbitmq_publish_filenames_client._queue,
                    durable=True,
                )
                channel.confirm_delivery()
                channel.basic_publish(
                    exchange="",
                    routing_key=rabbitmq_publish_filenames_client._queue,
                    body=args[0],
                    properties=pika.BasicProperties(
                        delivery_mode=pika.DeliveryMode.Persistent,
                    ),
                )

    monkeypatch.setattr(
        rabbitmq_publish_filenames_client,
        "_amqp_publish",
        mocked_partially_failed_basic_publish,
    )

    with caplog.at_level("ERROR"):
        publish_successes = rabbitmq_publish_filenames_client.publish(filenames)

        successes_filenames = [
            filename
            for filename, success in zip(filenames, publish_successes)
            if success
        ]
        assert not all(publish_successes)
        assert any(publish_successes)
        assert publish_successes[2] == False
        assert "Failed to publish" in caplog.text

    pika_conn, queue = raw_rabbitmq_pika_conn_config

    channel = pika_conn.channel()
    for filename in successes_filenames:
        method_frame, _, body = channel.basic_get(queue=queue)
        assert method_frame is not None
        assert body.decode() == filename
        channel.basic_ack(method_frame.delivery_tag)
