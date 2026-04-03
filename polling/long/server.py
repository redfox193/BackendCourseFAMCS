import asyncio
import time
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

messages: list[dict] = []
waiters: list[asyncio.Future] = []


class Message(BaseModel):
    author: str
    text: str


def notify_waiters(message: dict) -> None:
    for future in waiters:
        if not future.done():
            future.set_result(message)
    waiters.clear()


@app.post('/message')
async def post_message(msg: Message) -> dict:
    message = {
        'id': len(messages),
        'author': msg.author,
        'text': msg.text,
        'ts': time.time(),
    }
    messages.append(message)
    notify_waiters(message)
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
