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
    "filenames",
    [random_filenames() for _ in range(5)],
)
def test_publish_batch_success(
    rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filenames: list[str],
):
    assert all(rabbitmq_publish_filenames_client.publish(filenames))

    pika_conn, queue = raw_rabbitmq_pika_conn_config

    all_filenames = []

    channel = pika_conn.channel()
    while len(all_filenames) < len(filenames):
        method_frame, _, body = channel.basic_get(queue=queue)
        assert method_frame is not None
        all_filenames.append(body.decode())
        channel.basic_ack(method_frame.delivery_tag)

    assert sorted(all_filenames) == sorted(filenames)
