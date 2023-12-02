from src.deployments.script.main import traverse_files
from src.deployments.script.config import ProjectConfig
from typing import Type
import pytest
from .utils import random_csv_filenames
import pathlib
from pytest import MonkeyPatch


@pytest.mark.parametrize(
    "random_csv_filenames",
    [random_csv_filenames() for _ in range(5)],
)
def test_traverse_files_show_all_files(
    mock_project_config: Type[ProjectConfig],
    random_csv_filenames: list[str],
    monkeypatch: MonkeyPatch,
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
    assert set(traverse_files()) == set(
        [
            str(pathlib.Path(mock_project_config.TARGET_FILE_DIR).joinpath(filename))
            for filename in random_csv_filenames
        ]
    )


@pytest.mark.parametrize(
    "random_csv_filenames",
    [random_csv_filenames() for _ in range(5)],
)
def test_traverse_files_show_top_level_files_only(
    mock_project_config: Type[ProjectConfig],
    random_csv_filenames: list[str],
    monkeypatch: MonkeyPatch,
):
    temp_dir = pathlib.Path(mock_project_config.TARGET_FILE_DIR) / "temp"
    for i, path in enumerate(
        [
            pathlib.Path(mock_project_config.TARGET_FILE_DIR).joinpath(filename)
            for filename in random_csv_filenames
        ]
    ):
        if i != 4:
            path.touch()
        else:
            temp_dir.mkdir()
            (temp_dir / path.name).touch()

    monkeypatch.setattr(
        ProjectConfig, "TARGET_FILE_DIR", mock_project_config.TARGET_FILE_DIR
    )
    monkeypatch.setattr(
        ProjectConfig,
        "TARGET_FILE_EXTENSION",
        mock_project_config.TARGET_FILE_EXTENSION,
    )

    assert set(traverse_files()) == set(
        [
            str(pathlib.Path(mock_project_config.TARGET_FILE_DIR).joinpath(filename))
            for i, filename in enumerate(random_csv_filenames)
            if i != 4
        ]
    )


@pytest.mark.xfail(reason="Subdirectories are not supported", strict=True)
@pytest.mark.parametrize(
    "random_csv_filenames",
    [random_csv_filenames() for _ in range(5)],
)
def test_traverse_files_show_all_recursive_files(
    mock_project_config: Type[ProjectConfig],
    random_csv_filenames: list[str],
    monkeypatch: MonkeyPatch,
):
    all_path = []
    temp_dir = pathlib.Path(mock_project_config.TARGET_FILE_DIR) / "temp"
    for i, path in enumerate(
        [
            pathlib.Path(mock_project_config.TARGET_FILE_DIR).joinpath(filename)
            for filename in random_csv_filenames
        ]
    ):
        if i != 4:
            path.touch()
            all_path.append(path)
        else:
            temp_dir.mkdir()
            new_path = temp_dir / path.name
            new_path.touch()
            all_path.append(new_path)

    monkeypatch.setattr(
        ProjectConfig, "TARGET_FILE_DIR", mock_project_config.TARGET_FILE_DIR
    )
    monkeypatch.setattr(
        ProjectConfig,
        "TARGET_FILE_EXTENSION",
        mock_project_config.TARGET_FILE_EXTENSION,
    )

    assert set(traverse_files()) == set([str(path) for path in all_path])
