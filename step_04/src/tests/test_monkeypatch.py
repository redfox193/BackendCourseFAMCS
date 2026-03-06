from app import config

from unittest.mock import AsyncMock

from app.services.alert_service import check_and_alert_async
from app.services.notification import NotificationSender


def test_setenv_alerts_disabled(monkeypatch):
    """monkeypatch.setenv — подмена переменной окружения."""
    monkeypatch.setenv("WEATHER_ALERTS_ENABLED", "0")
    assert config.is_alerts_enabled() is False


def test_setenv_alerts_enabled(monkeypatch):
    monkeypatch.setenv("WEATHER_ALERTS_ENABLED", "1")
    assert config.is_alerts_enabled() is True


def test_setenv_threshold(monkeypatch):
    """Порог температуры читается из env."""
    monkeypatch.setenv("ALERT_TEMP_THRESHOLD", "40")
    assert config.get_alert_threshold() == 40


def test_setattr_api_url(monkeypatch):
    """monkeypatch.setattr — подмена функции или атрибута."""
    monkeypatch.setattr(config, "get_api_base_url", lambda: "http://fake-api.test")
    # Патчим в модуле; вызов через модуль использует подмену
    assert config.get_api_base_url() == "http://fake-api.test"


def test_setattr_api_url_alternative(monkeypatch):
    """monkeypatch.setattr — подмена функции или атрибута."""
    monkeypatch.setattr("app.config.get_api_base_url", lambda: "http://fake-api.test")
    # Патчим в модуле; вызов через модуль использует подмену
    assert config.get_api_base_url() == "http://fake-api.test"


def test_setattr_os_getenv(monkeypatch):
    """Подмена os.getenv для изоляции от реального окружения."""
    def fake_getenv(key, default=None):
        return {"WEATHER_ALERTS_ENABLED": "0", "ALERT_TEMP_THRESHOLD": "99"}.get(key, default)

    monkeypatch.setattr("app.config.os.getenv", fake_getenv)
    assert config.is_alerts_enabled() is False
    assert config.get_alert_threshold() == 99


async def test_async_monkeypatch_with_function(monkeypatch):
    """подмена async-функции своей реализацией"""

    async def fake_fetch_weather(city: str) -> dict:
        return {"temp": 42}

    async def fake_send_async(self, message: str, user_id: str) -> bool:
        return True

    # Строковый вариант: как у patch, но через monkeypatch
    monkeypatch.setattr(
        "app.services.alert_service.fetch_weather_async",
        fake_fetch_weather,
    )
    # Отключаем реальные HTTP-запросы уведомлений
    monkeypatch.setattr(
        "app.services.notification.NotificationSender.send_async",
        fake_send_async,
    )

    result = await check_and_alert_async("Rome", "user-1")

    assert result["alert_sent"] is True
    assert result["temp"] == 42


async def test_async_monkeypatch_with_asyncmock(monkeypatch):
    """monkeypatch + AsyncMock"""
    async_fetch_mock = AsyncMock(return_value={"temp": 37})
    send_async_mock = AsyncMock(return_value=True)

    monkeypatch.setattr(
        "app.services.alert_service.fetch_weather_async",
        async_fetch_mock,
    )
    monkeypatch.setattr(
        "app.services.notification.NotificationSender.send_async",
        send_async_mock,
    )

    result = await check_and_alert_async("Berlin", "user-2")

    assert result["alert_sent"] is True
    assert result["temp"] == 37
    async_fetch_mock.assert_awaited_once_with("Berlin")
    send_async_mock.assert_awaited_once()
