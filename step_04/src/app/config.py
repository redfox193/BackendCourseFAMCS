"""Конфигурация приложения. Читает настройки из переменных окружения."""
import os


def is_alerts_enabled() -> bool:
    """Включены ли оповещения о погоде (feature flag)."""
    return os.getenv("WEATHER_ALERTS_ENABLED", "1") == "1"


def get_alert_threshold() -> int:
    """Порог температуры (°C) для срабатывания алерта."""
    return int(os.getenv("ALERT_TEMP_THRESHOLD", "35"))


def get_api_base_url() -> str:
    """Базовый URL внешнего API погоды."""
    return os.getenv("WEATHER_API_URL", "https://api.weather.example")
