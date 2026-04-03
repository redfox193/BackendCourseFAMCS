import asyncio
import json
import random
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def event_generator(request: Request, last_event_id) -> AsyncIterator[str]:
    event_id = last_event_id if not None else 0
    while True:
        if await request.is_disconnected():
            print(f'[SSE] client disconnected at id={event_id}')
            break

        price = round(random.uniform(90, 110), 2)
        payload = json.dumps({'usd': price})

        yield f'id: {event_id}\nevent: price\ndata: {payload}\n\n'

        event_id += 1
        await asyncio.sleep(0.5)


@app.get('/events')
async def sse_endpoint(request: Request) -> StreamingResponse:
    last_event_id = int(request.headers.get('last-event-id', -1)) + 1
    return StreamingResponse(
        event_generator(request, last_event_id),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        },
    )
