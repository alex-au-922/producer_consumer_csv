from pytest import MonkeyPatch
import pika
from src.adapters.publish_filenames.rabbitmq import RabbitMQPublishFilenamesClient
from .utils import random_filenames


def test_close_conn_failed(
    rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
    monkeypatch: MonkeyPatch,
):
    rabbitmq_publish_filenames_client.publish(random_filenames()[0])

    assert rabbitmq_publish_filenames_client._conn is not None

    def mock_failed_close(
        self,
        *args,
        **kwargs,
    ) -> None:
        raise Exception("Failed to close!")

    monkeypatch.setattr(pika.BlockingConnection, "close", mock_failed_close)
    assert not rabbitmq_publish_filenames_client.close()
