"""Сервис отправки уведомлений (email, push и т.д.)."""
import httpx


class NotificationSender:
    """Отправляет уведомления во внешний сервис."""

    def __init__(self, webhook_url: str = "https://notify.example/send"):
        self.webhook_url = webhook_url

    def send(self, message: str, user_id: str) -> bool:
        """Отправить уведомление. Возвращает True при успехе."""
        response = httpx.post(
            self.webhook_url,
            json={"message": message, "user_id": user_id},
        )
        return response.status_code == 200

    async def send_async(self, message: str, user_id: str) -> bool:
        """Асинхронная отправка."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.webhook_url,
                json={"message": message, "user_id": user_id},
            )
            return response.status_code == 200
