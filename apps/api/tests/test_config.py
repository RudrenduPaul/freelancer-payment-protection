from pathlib import Path


def test_env_file_is_absolute_and_inside_api_app_dir():
    from apps.api.app.config import Settings

    env_file = Settings.model_config["env_file"]
    path = Path(env_file)

    api_dir = Path(__file__).resolve().parents[1]
    assert path.is_absolute()
    assert path == api_dir / ".env"
    assert api_dir in path.parents


def test_env_file_ignores_working_directory(tmp_path, monkeypatch):
    from apps.api.app.config import Settings

    before = Settings.model_config["env_file"]
    monkeypatch.chdir(tmp_path)
    assert Settings.model_config["env_file"] == before
    assert tmp_path not in Path(before).parents
