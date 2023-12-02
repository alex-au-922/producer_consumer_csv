from src.deployments.script.main import main
from src.deployments.script.config import ProjectConfig, RabbitMQConfig
from typing import Type
import pytest
from .utils import random_csv_filenames
import pathlib
from pytest import MonkeyPatch, LogCaptureFixture


@pytest.mark.parametrize(
    "random_csv_filenames",
    [random_csv_filenames() for _ in range(5)],
)
def test_main_flow_no_failed_files(
    mock_rabbitmq_config: Type[RabbitMQConfig],
    mock_project_config: Type[ProjectConfig],
    random_csv_filenames: list[str],
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    for path in [
        pathlib.Path(mock_project_config.TARGET_FILE_DIR).joinpath(filename)
        for filename in random_csv_filenames
    ]:
        path.touch()

    monkeypatch.setattr(
        ProjectConfig, "TARGET_FILE_DIR", mock_project_config.TARGET_FILE_DIR
    )
    monkeypatch.setattr(
        ProjectConfig,
        "TARGET_FILE_EXTENSION",
        mock_project_config.TARGET_FILE_EXTENSION,
    )
    monkeypatch.setattr(RabbitMQConfig, "HOST", mock_rabbitmq_config.HOST)
    monkeypatch.setattr(RabbitMQConfig, "PORT", mock_rabbitmq_config.PORT)
    monkeypatch.setattr(RabbitMQConfig, "USERNAME", mock_rabbitmq_config.USERNAME)
    monkeypatch.setattr(RabbitMQConfig, "PASSWORD", mock_rabbitmq_config.PASSWORD)
    monkeypatch.setattr(RabbitMQConfig, "QUEUE", mock_rabbitmq_config.QUEUE)

    with caplog.at_level("INFO"):
        assert main() is None
        assert "Successfully published all filenames" in caplog.text
