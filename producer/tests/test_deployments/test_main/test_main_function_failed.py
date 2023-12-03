from src.deployments.script.main import main
from src.deployments.script.config import ProjectConfig
from typing import Type
import pytest
from .utils import random_csv_filenames
import pathlib
from pytest import MonkeyPatch, LogCaptureFixture


@pytest.mark.parametrize(
    "random_csv_filenames",
    [random_csv_filenames() for _ in range(5)],
)
def test_main_flow_has_failed_files(
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

    monkeypatch.setattr(
        "src.adapters.publish_filenames.rabbitmq.RabbitMQPublishFilenamesClient.publish",
        lambda self, filename: False,
    )
    with caplog.at_level("ERROR"):
        with pytest.raises(Exception, match="^Failed to publish filenames.*$"):
            main()
        assert "Failed to publish filenames" in caplog.text
