import os

import pytest

@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("TESTING", "1")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("APP_BASE_URL", "http://test")

    if not os.getenv("DATABASE_URL"):
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///db/test.db")

    from common.settings import get_settings

    get_settings.cache_clear()
