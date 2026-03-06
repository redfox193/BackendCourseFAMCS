from unittest.mock import patch

import pytest
from app.services.alert_service import check_and_alert, get_weather_summary


@patch("app.services.alert_service.WeatherClient")
def test_check_alert_no_alert_when_temp_low(MockWeatherClient):
    """Мок класса WeatherClient — подменяем конструктор и метод get_weather."""
    MockWeatherClient.return_value.get_weather.return_value = {"temp": 25, "condition": "sunny"}

    result = check_and_alert("Moscow", "user-1")

    assert result["alert_sent"] is False
    assert result["temp"] == 25
    MockWeatherClient.return_value.get_weather.assert_called_once_with("Moscow")


@patch("app.services.alert_service.NotificationSender")
@patch("app.services.alert_service.WeatherClient")
def test_check_alert_sends_when_high_temp(MockWeatherClient, MockNotificationSender):
    """Два патча — порядок аргументов обратный порядку декораторов."""
    MockWeatherClient.return_value.get_weather.return_value = {"temp": 40}
    MockNotificationSender.return_value.send.return_value = True

    result = check_and_alert("Dubai", "user-2")

    assert result["alert_sent"] is True
    assert result["temp"] == 40
    assert "Жара" in result["message"]
    MockNotificationSender.return_value.send.assert_called_once()
    call_args = MockNotificationSender.return_value.send.call_args
    assert "Dubai" in call_args[0][0]
    assert call_args[0][1] == "user-2"


@patch("app.services.alert_service.WeatherClient")
def test_get_weather_summary(MockWeatherClient):
    """Мок функции/метода — return_value задаёт ответ."""
    MockWeatherClient.return_value.get_weather.return_value = {
        "temp": 18,
        "condition": "cloudy",
    }

    summary = get_weather_summary("London")

    assert summary == "London: 18°C, cloudy"
    MockWeatherClient.return_value.get_weather.assert_called_once_with("London")


@patch("app.services.alert_service.WeatherClient")
def test_side_effect_exception(MockWeatherClient):
    """side_effect — симуляция исключения при вызове."""
    MockWeatherClient.return_value.get_weather.side_effect = ConnectionError("API down")

    with pytest.raises(ConnectionError):
        get_weather_summary("Paris")
