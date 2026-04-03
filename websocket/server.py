import random
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

participants: dict[str, WebSocket] = {}
SUPPORTED_PROTOCOLS = {"chat_v1", "chat_v2"}


def encode_frame(username: str, voice_data: bytes) -> bytes:
    name_bytes = username.encode()
    return bytes([len(name_bytes)]) + name_bytes + voice_data


async def broadcast(sender: str, frame: bytes) -> None:
    disconnected = []
    for username, ws in participants.items():
        if username == sender:
            continue
        try:
            await ws.send_bytes(frame)
        except Exception:
            disconnected.append(username)
    for username in disconnected:
        participants.pop(username, None)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    participants.clear()


app = FastAPI(lifespan=lifespan)


@app.websocket("/enter")
async def enter_voice_chat(ws: WebSocket, username: str) -> None:
    requested = set(ws.headers.get("sec-websocket-protocol", "").split(", ")) & SUPPORTED_PROTOCOLS
    chosen = random.choice(list(requested)) if requested else None

    await ws.accept(subprotocol=chosen)
    print(f"[+] {username} joined with protocol={chosen}")

    if not chosen:
        await ws.send_text("No supported protocol found.")
        await ws.close()
        return

    if username in participants:
        await ws.send_text(f"Username '{username}' is already taken.")
        await ws.close()
        return

    participants[username] = ws

    try:
        while True:
            voice_data: bytes = await ws.receive_bytes()

            if chosen == "chat_v2":
                name_len = voice_data[0]
                voice_data = voice_data[1 + name_len:]

            frame = encode_frame(username, voice_data)
            await broadcast(username, frame)

    except WebSocketDisconnect:
        participants.pop(username, None)
        print(f"[-] {username} left.")
