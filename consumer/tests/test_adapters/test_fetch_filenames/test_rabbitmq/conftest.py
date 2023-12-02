from src.adapters.fetch_filenames.rabbitmq import RabbitMQFetchFilenamesClient
from src.deployments.scripts.config import RabbitMQConfig
import pika
import pytest
from pytest import MonkeyPatch


@pytest.fixture(scope="function")
def rabbitmq_fetch_filenames_client() -> RabbitMQFetchFilenamesClient:
    return RabbitMQFetchFilenamesClient(
        host=RabbitMQConfig.HOST,
        port=RabbitMQConfig.PORT,
        credentials_service=lambda: (RabbitMQConfig.USERNAME, RabbitMQConfig.PASSWORD),
        queue=RabbitMQConfig.QUEUE,
        polling_timeout=RabbitMQConfig.POLLING_TIMEOUT,
    )


@pytest.fixture(scope="function")
def raw_rabbitmq_pika_conn_config() -> tuple[pika.BaseConnection, str]:
    pika_conn = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RabbitMQConfig.HOST,
            port=RabbitMQConfig.PORT,
            credentials=pika.PlainCredentials(
                RabbitMQConfig.USERNAME, RabbitMQConfig.PASSWORD
            ),
        )
    )
    return pika_conn, RabbitMQConfig.QUEUE
