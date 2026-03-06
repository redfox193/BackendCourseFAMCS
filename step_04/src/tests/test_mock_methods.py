from unittest.mock import patch, Mock

from app.services.weather_client import WeatherClient
from app.services.notification import NotificationSender


@patch.object(WeatherClient, "get_weather")
def test_patch_object_method(mock_get_weather):
    """patch.object(Class, "method") — подмена метода конкретного класса."""
    mock_get_weather.return_value = {"temp": 30, "condition": "hot"}

    client = WeatherClient()
    result = client.get_weather("Cairo")

    assert result["temp"] == 30
    mock_get_weather.assert_called_once_with("Cairo")


@patch("app.services.weather_client.httpx.get")
def test_patch_httpx_get(mock_httpx_get):
    """Патчим httpx.get — место использования в weather_client."""
    mock_response = Mock()
    mock_response.json.return_value = {"temp": 22, "condition": "windy"}
    mock_response.raise_for_status = Mock()
    mock_httpx_get.return_value = mock_response

    client = WeatherClient(base_url="http://fake")
    result = client.get_weather("Berlin")

    assert result["temp"] == 22
    mock_httpx_get.assert_called_once()
    call_kwargs = mock_httpx_get.call_args
    assert "Berlin" in str(call_kwargs)


@patch.object(NotificationSender, "send")
def test_notification_send_called(mock_send):
    """Проверка вызова метода send с правильными аргументами."""
    mock_send.return_value = True

    sender = NotificationSender(webhook_url="http://test")
    sender.send("Test message", "user-123")

    mock_send.assert_called_once_with("Test message", "user-123")


@patch.object(NotificationSender, "send")
def test_call_count_and_call_args(mock_send):
    """call_count, call_args — детальная проверка вызовов."""
    mock_send.return_value = True

    sender = NotificationSender()
    sender.send("First", "u1")
    sender.send("Second", "u2")

    assert mock_send.call_count == 2
    assert mock_send.call_args_list[0][0] == ("First", "u1")
    assert mock_send.call_args_list[1][0] == ("Second", "u2")
