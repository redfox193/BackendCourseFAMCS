from unittest.mock import AsyncMock, patch

from app.services.alert_service import check_and_alert_async
from app.services.notification import NotificationSender


@patch("app.services.alert_service.fetch_weather_async", new_callable=AsyncMock)
@patch("app.services.alert_service.NotificationSender")
async def test_check_and_alert_async(MockNotificationSender, mock_fetch_weather):
    mock_fetch_weather.return_value = {"temp": 39}
    MockNotificationSender.return_value.send_async = AsyncMock(return_value=True)

    result = await check_and_alert_async("Phoenix", "user-async")

    assert result["alert_sent"] is True
    assert result["temp"] == 39
    mock_fetch_weather.assert_awaited_once_with("Phoenix")
    MockNotificationSender.return_value.send_async.assert_awaited_once()


@patch("app.services.alert_service.fetch_weather_async", new_callable=AsyncMock)
async def test_async_no_alert_when_temp_ok(mock_fetch_weather):
    mock_fetch_weather.return_value = {"temp": 20}

    result = await check_and_alert_async("Amsterdam", "user-1")

    assert result["alert_sent"] is False
    assert result["temp"] == 20
