"""
5. Мок вызовов сторонних сервисов.
HTTP-клиенты, внешние API — изоляция от сети.
"""
from unittest.mock import patch

import pytest
from app.services.alert_service import check_and_alert
from app.services.weather_client import WeatherClient


@patch("app.services.weather_client.httpx.get")
def test_weather_client_mocked_http(mock_get):
    """Мок httpx.get — никаких реальных HTTP-запросов."""
    mock_response = mock_get.return_value
    mock_response.json.return_value = {"temp": 28, "condition": "sunny"}
    mock_response.raise_for_status = lambda: None

    client = WeatherClient(base_url="http://fake")
    data = client.get_weather("Tokyo")

    assert data["temp"] == 28
    mock_get.assert_called_once_with(
        "http://fake/weather",
        params={"city": "Tokyo"},
    )


@patch("app.services.notification.httpx.post")
def test_notification_mocked_http(mock_post):
    """Мок отправки уведомлений — внешний webhook не вызывается."""
    mock_response = mock_post.return_value
    mock_response.status_code = 200

    from app.services.notification import NotificationSender

    sender = NotificationSender(webhook_url="http://fake-webhook")
    result = sender.send("Alert!", "user-1")

    assert result is True
    mock_post.assert_called_once_with(
        "http://fake-webhook",
        json={"message": "Alert!", "user_id": "user-1"},
    )


@patch("app.services.alert_service.NotificationSender")
@patch("app.services.alert_service.WeatherClient")
def test_full_flow_no_network(MockWeatherClient, MockNotificationSender):
    """Полный flow check_and_alert без единого сетевого вызова."""
    MockWeatherClient.return_value.get_weather.return_value = {"temp": 36}
    MockNotificationSender.return_value.send.return_value = True

    result = check_and_alert("Mumbai", "user-99")

    assert result["alert_sent"] is True
    assert "Mumbai" in result["message"]
    MockWeatherClient.return_value.get_weather.assert_called_once_with("Mumbai")
    MockNotificationSender.return_value.send.assert_called_once()


@patch("app.services.weather_client.httpx.get")
def test_http_error_propagation(mock_get):
    """Проверка: исключение от API пробрасывается наверх."""
    mock_get.return_value.raise_for_status.side_effect = Exception("503 Service Unavailable")
    mock_get.return_value.json.return_value = {}

    client = WeatherClient(base_url="http://fake")

    with pytest.raises(Exception, match="503"):
        client.get_weather("AnyCity")
