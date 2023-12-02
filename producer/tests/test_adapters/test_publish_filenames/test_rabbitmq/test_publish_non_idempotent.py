import pytest
from .utils import random_filenames
from src.adapters.publish_filenames.rabbitmq import RabbitMQPublishFilenamesClient
import pika
import pytest


@pytest.mark.smoke
@pytest.mark.parametrize("filename", random_filenames())
def test_publish_single_non_idempotent(
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

    assert rabbitmq_publish_filenames_client.publish(filename)
    assert rabbitmq_publish_filenames_client.publish(filename)

    method_frame, _, body = channel.basic_get(queue=queue)
    assert method_frame is not None
    assert body.decode() == filename
    channel.basic_ack(method_frame.delivery_tag)

    method_frame, _, body = channel.basic_get(queue=queue)
    assert method_frame is None
    assert body is None


@pytest.mark.smoke
@pytest.mark.parametrize("filenames", [random_filenames() for _ in range(5)])
def test_publish_batch_non_idempotent(
    rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filenames: list[str],
):
    assert all(rabbitmq_publish_filenames_client.publish(filenames))
    assert all(rabbitmq_publish_filenames_client.publish(filenames))

    pika_conn, queue = raw_rabbitmq_pika_conn_config
    filenames_counter = {filename: 0 for filename in filenames}
    channel = pika_conn.channel()
    method_frame, _, body = channel.basic_get(queue=queue)
    while method_frame is not None:
        filenames_counter[body.decode()] += 1
        channel.basic_ack(method_frame.delivery_tag)
        method_frame, _, body = channel.basic_get(queue=queue)

    assert all(count == 2 for count in filenames_counter.values())
