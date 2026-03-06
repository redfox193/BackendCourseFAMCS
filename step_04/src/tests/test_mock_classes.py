from unittest.mock import patch

from app.services.alert_service import check_and_alert


class FakeWeatherClient:
    """Фейк-клиент вместо реального WeatherClient."""

    def __init__(self, *args, **kwargs):
        pass

    def get_weather(self, city: str):
        return {"temp": 38, "condition": "heatwave"}


@patch("app.services.alert_service.WeatherClient", FakeWeatherClient)
@patch("app.services.alert_service.NotificationSender")
def test_mock_class_with_fake(MockNotificationSender):
    """Подмена класса на фейк — все инстансы будут FakeWeatherClient."""
    MockNotificationSender.return_value.send.return_value = True

    result = check_and_alert("Riyadh", "user-x")

    assert result["temp"] == 38
    assert result["alert_sent"] is True
    MockNotificationSender.return_value.send.assert_called_once()


@patch("app.services.alert_service.WeatherClient")
def test_mock_constructor_returns_controlled_instance(MockWeatherClient):
    MockWeatherClient.return_value.get_weather.return_value = {"temp": 5, "condition": "cold"}

    result = check_and_alert("Helsinki", "user-y")

    assert result["temp"] == 5
    assert result["alert_sent"] is False
    MockWeatherClient.assert_called_once()  # конструктор вызван ровно раз
