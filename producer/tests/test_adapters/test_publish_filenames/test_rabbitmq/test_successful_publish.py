import pytest
from .utils import random_filenames
from src.adapters.publish_filenames.rabbitmq import RabbitMQPublishFilenamesClient
import pika
import pytest


@pytest.mark.smoke
@pytest.mark.parametrize("filename", random_filenames())
def test_publish_single_success(
    rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filename: str,
):
    assert rabbitmq_publish_filenames_client.publish(filename)

    pika_conn, queue = raw_rabbitmq_pika_conn_config

    channel = pika_conn.channel()
    method_frame, _, body = channel.basic_get(queue=queue)
    assert method_frame is not None
    assert body.decode() == filename
    channel.basic_ack(method_frame.delivery_tag)


@pytest.mark.smoke
@pytest.mark.parametrize(
    "random_filenames",
    [random_filenames() for _ in range(5)],
)
def test_publish_batch_success(
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
