"""Бизнес-логика: проверка погоды и отправка алертов."""
from app.config import is_alerts_enabled, get_alert_threshold
from app.services.weather_client import WeatherClient, fetch_weather_async
from app.services.notification import NotificationSender


def check_and_alert(city: str, user_id: str) -> dict:
    """
    Проверить погоду и отправить алерт при превышении порога.
    Возвращает {"alert_sent": bool, "temp": int, "message": str}.
    """
    if not is_alerts_enabled():
        return {"alert_sent": False, "temp": None, "message": "Alerts disabled"}

    client = WeatherClient()
    weather = client.get_weather(city)
    temp = weather.get("temp", 0)
    threshold = get_alert_threshold()

    if temp >= threshold:
        sender = NotificationSender()
        msg = f"Жара! В {city} {temp}°C"
        sent = sender.send(msg, user_id)
        return {"alert_sent": sent, "temp": temp, "message": msg}

    return {"alert_sent": False, "temp": temp, "message": f"OK: {temp}°C"}


async def check_and_alert_async(city: str, user_id: str) -> dict:
    """Асинхронная версия check_and_alert."""
    if not is_alerts_enabled():
        return {"alert_sent": False, "temp": None, "message": "Alerts disabled"}

    weather = await fetch_weather_async(city)
    temp = weather.get("temp", 0)
    threshold = get_alert_threshold()

    if temp >= threshold:
        sender = NotificationSender()
        msg = f"Жара! В {city} {temp}°C"
        sent = await sender.send_async(msg, user_id)
        return {"alert_sent": sent, "temp": temp, "message": msg}

    return {"alert_sent": False, "temp": temp, "message": f"OK: {temp}°C"}


def get_weather_summary(city: str) -> str:
    """Формирует текстовое описание погоды. Использует WeatherClient."""
    client = WeatherClient()
    data = client.get_weather(city)
    temp = data.get("temp", "?")
    condition = data.get("condition", "unknown")
    return f"{city}: {temp}°C, {condition}"
