from app.core.config import PROJECT_ROOT, settings


def test_default_app_environment():
    assert settings.app_env in {"development", "production", "testing"}


def test_debug_is_boolean():
    assert isinstance(settings.debug, bool)


def test_database_url_uses_expected_backend():
    from sqlalchemy.engine import make_url

    url = make_url(settings.database_url)
    assert url.get_backend_name() == "sqlite"


def test_project_root_exists():
    assert PROJECT_ROOT.exists()
