import pytest
from .utils import random_filenames
from src.adapters.publish_filenames.rabbitmq import RabbitMQPublishFilenamesClient
from src.deployments.script.config import RabbitMQConfig
import pika
from pytest import MonkeyPatch


@pytest.mark.smoke
@pytest.mark.parametrize("filename", random_filenames())
def test_publish_single_failed_conn(
    rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filename: str,
    monkeypatch: MonkeyPatch,
):
    def mocked_failed_conn(
        self,
        *args,
        **kwargs,
    ) -> None:
        raise Exception("Failed to connect")

    monkeypatch.setattr(pika.BlockingConnection, "__init__", mocked_failed_conn)

    with pytest.raises(Exception) as e:
        assert not rabbitmq_publish_filenames_client.publish(filename)
        assert e.value == "Failed to connect"

    pika_conn, queue = raw_rabbitmq_pika_conn_config

    channel = pika_conn.channel()
    method_frame, _, body = channel.basic_get(queue=queue)
    assert method_frame is None
    assert body is None


@pytest.mark.smoke
@pytest.mark.parametrize(
    "random_filenames",
    [random_filenames() for _ in range(5)],
)
def test_publish_batch_failed_conn(
    rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    random_filenames: list[str],
    monkeypatch: MonkeyPatch,
):
    def mocked_failed_conn(
        self,
        *args,
        **kwargs,
    ) -> None:
        raise Exception("Failed to connect")

    monkeypatch.setattr(pika.BlockingConnection, "__init__", mocked_failed_conn)

    with pytest.raises(Exception) as e:
        assert not any(rabbitmq_publish_filenames_client.publish(random_filenames))
        assert e.value == "Failed to connect"

    pika_conn, queue = raw_rabbitmq_pika_conn_config

    channel = pika_conn.channel()
    for _ in random_filenames:
        method_frame, _, body = channel.basic_get(queue=queue)
        assert method_frame is None
        assert body is None


@pytest.mark.smoke
@pytest.mark.parametrize("filename", random_filenames())
def test_publish_single_wrong_credentials(
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filename: str,
):
    rabbitmq_publish_filenames_client = RabbitMQPublishFilenamesClient(
        host=RabbitMQConfig.HOST,
        port=RabbitMQConfig.PORT,
        credentials_service=lambda: ("wrong", "wrong"),
        queue=RabbitMQConfig.QUEUE,
    )

    with pytest.raises(Exception) as e:
        assert not rabbitmq_publish_filenames_client.publish(filename)
        assert "ACCESS_REFUSED" in e.value and "403" in e.value

    pika_conn, queue = raw_rabbitmq_pika_conn_config
    channel = pika_conn.channel()
    method_frame, _, body = channel.basic_get(queue=queue)
    assert method_frame is None
    assert body is None


@pytest.mark.slow
@pytest.mark.smoke
@pytest.mark.parametrize("filename", random_filenames())
def test_publish_single_wrong_host(
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    filename: str,
):
    rabbitmq_publish_filenames_client = RabbitMQPublishFilenamesClient(
        host="wrong",
        port=RabbitMQConfig.PORT,
        credentials_service=lambda: (RabbitMQConfig.USERNAME, RabbitMQConfig.PASSWORD),
        queue=RabbitMQConfig.QUEUE,
    )

    with pytest.raises(Exception) as e:
        assert not rabbitmq_publish_filenames_client.publish(filename)
        assert "ACCESS_REFUSED" in e.value and "403" in e.value

    pika_conn, queue = raw_rabbitmq_pika_conn_config
    channel = pika_conn.channel()
    method_frame, _, body = channel.basic_get(queue=queue)
    assert method_frame is None
    assert body is None


@pytest.mark.slow
@pytest.mark.parametrize("filename", random_filenames())
def test_publish_single_failed_conn_reset_conn(
    rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
    filename: str,
    monkeypatch: MonkeyPatch,
):
    assert rabbitmq_publish_filenames_client.publish(filename)
    conn = rabbitmq_publish_filenames_client._conn

    def mock_failed_basic_publish(
        self,
        *args,
        **kwargs,
    ) -> None:
        raise Exception("Failed to publish!")

    monkeypatch.setattr(
        pika.channel.Channel, "basic_publish", mock_failed_basic_publish
    )

    assert not rabbitmq_publish_filenames_client.publish(filename)

    monkeypatch.undo()

    assert rabbitmq_publish_filenames_client.publish(filename)
    assert rabbitmq_publish_filenames_client._conn != conn


@pytest.mark.slow
@pytest.mark.parametrize(
    "random_filenames",
    [random_filenames() for _ in range(5)],
)
def test_publish_batch_failed_conn_reset_conn(
    rabbitmq_publish_filenames_client: RabbitMQPublishFilenamesClient,
    random_filenames: list[str],
    monkeypatch: MonkeyPatch,
):
    assert all(rabbitmq_publish_filenames_client.publish(random_filenames))
    conn = rabbitmq_publish_filenames_client._conn

    def mock_failed_basic_publish(
        self,
        *args,
        **kwargs,
    ) -> None:
        raise Exception("Failed to publish!")

    monkeypatch.setattr(
        pika.channel.Channel, "basic_publish", mock_failed_basic_publish
    )

    assert not any(rabbitmq_publish_filenames_client.publish(random_filenames))

    monkeypatch.undo()

    assert rabbitmq_publish_filenames_client.publish(random_filenames)
    assert rabbitmq_publish_filenames_client._conn != conn
