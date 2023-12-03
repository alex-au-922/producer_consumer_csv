from typing import Type
from src.deployments.script.config import RabbitMQConfig, ProjectConfig
import pika
import pytest
from pytest import TempdirFactory
import pathlib


@pytest.fixture(scope="session")
def mock_project_config(tmpdir_factory: TempdirFactory) -> None:
    class MockedProjectConfig(ProjectConfig):
        TARGET_FILE_DIR = str(tmpdir_factory.mktemp("artifact"))
        TARGET_FILE_EXTENSION = ProjectConfig.TARGET_FILE_EXTENSION

    return MockedProjectConfig


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


@pytest.fixture(scope="function", autouse=True)
def setup_teardown_rabbitmq_queue(
    raw_rabbitmq_pika_conn_config: tuple[pika.BaseConnection, str],
) -> None:
    pika_conn, queue = raw_rabbitmq_pika_conn_config

    channel = pika_conn.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.queue_purge(queue=queue)
    yield
    channel.queue_purge(queue=queue)


@pytest.fixture(scope="function", autouse=True)
def clean_artifact_dir(mock_project_config: Type[ProjectConfig]) -> None:
    def remove_files_in_dir(dir: pathlib.Path) -> None:
        for path in dir.rglob("*"):
            if path.is_file():
                path.unlink()
            else:
                remove_files_in_dir(path)
                path.rmdir()

    for path in pathlib.Path(mock_project_config.TARGET_FILE_DIR).rglob("*"):
        if path.is_file():
            path.unlink()
        else:
            remove_files_in_dir(path)
            path.rmdir()
    yield
    for path in pathlib.Path(mock_project_config.TARGET_FILE_DIR).rglob("*"):
        if path.is_file():
            path.unlink()
        else:
            remove_files_in_dir(path)
            path.rmdir()
