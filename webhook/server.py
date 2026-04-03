import asyncio
import time
import httpx
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

messages: list[dict] = []
waiters: list[asyncio.Future] = []
background_tasks: set[asyncio.Task] = set()
webhook_url: str | None = None


class Message(BaseModel):
    author: str
    text: str


class WebhookRegister(BaseModel):
    url: str


def notify_waiters(message: dict) -> None:
    for future in waiters:
        if not future.done():
            future.set_result(message)
    waiters.clear()


async def dispatch_webhook(message: dict) -> None:
    if not webhook_url:
        return
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(webhook_url, json=message)
    except httpx.RequestError as e:
        print(f"[server] webhook delivery failed: {e}")


@app.post('/webhook/register')
async def register_webhook(body: WebhookRegister) -> dict:
    global webhook_url
    webhook_url = body.url
    print(f'[server] webhook registered: {webhook_url}')
    return {'registered': webhook_url}


@app.post("/message")
async def post_message(msg: Message) -> dict:
    message = {
        "id": len(messages),
        "author": msg.author,
        "text": msg.text,
        "ts": time.time(),
    }
    messages.append(message)
    notify_waiters(message)

    task = asyncio.create_task(dispatch_webhook(message))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    return message


@app.get('/poll')
async def long_poll(since_id: int = -1, timeout: float = 30.0) -> dict:
    new_messages = [m for m in messages if m['id'] > since_id]
    if new_messages:
        return {'messages': new_messages, 'timed_out': False}

    loop = asyncio.get_event_loop()
    future: asyncio.Future = loop.create_future()
    waiters.append(future)

    try:
        message = await asyncio.wait_for(future, timeout=timeout)
        return {'messages': [message], 'timed_out': False}
    except asyncio.TimeoutError:
        waiters.remove(future)
        return {'messages': [], 'timed_out': True}
