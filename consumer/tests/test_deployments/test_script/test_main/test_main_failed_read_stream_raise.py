from typing import Iterator
from src.deployments.script.main import main
from src.deployments.script.config import RabbitMQConfig
from src.adapters.fetch_filenames_stream.rabbitmq import (
    RabbitMQFetchFilenameStreamClient,
)
import pytest
from pytest import MonkeyPatch, FixtureRequest
import pika


@pytest.mark.smoke
@pytest.mark.parametrize(
    "fixture_name",
    ["random_valid_csv_file"] * 5,
)
def test_main_flow_single_read_stream_failed_raise(
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
    fixture_name: str,
    request: FixtureRequest,
    monkeypatch: MonkeyPatch,
):
    random_csv_file: str = request.getfixturevalue(fixture_name)

    conn, queue = raw_rabbitmq_pika_conn_config
    channel = conn.channel()
    channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=random_csv_file,
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )

    def mock_read(self, *args, **kwargs) -> Iterator[str]:
        raise IOError("Cannot read stream!")

    monkeypatch.setattr(RabbitMQFetchFilenameStreamClient, "fetch_stream", mock_read)

    monkeypatch.setattr(RabbitMQConfig, "POLLING_TIMEOUT", 1)

    with pytest.raises(IOError, match="^Cannot read stream!$"):
        main()

    method_frame, _, body = channel.basic_get(queue=queue)
    assert method_frame is not None
    assert body.decode() == random_csv_file
