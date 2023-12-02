from src.adapters.publish_filenames.rabbitmq import RabbitMQPublishFilenamesClient
from .utils import random_filenames


def test_close_conn_successful(
    rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
):
    rabbitmq_publish_filenames_client.publish(random_filenames()[0])
    assert rabbitmq_publish_filenames_client._conn is not None
    assert rabbitmq_publish_filenames_client.close()


def test_none_conn_close_successful(
    rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
):
    assert rabbitmq_publish_filenames_client.close()
