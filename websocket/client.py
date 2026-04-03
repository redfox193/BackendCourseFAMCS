import asyncio
import random
import time
import websockets
import logging


logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.DEBUG,
)
logger = logging.getLogger("websockets")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


SERVER = "ws://127.0.0.1:8000/enter"
PROTOCOLS = ["chat_v1", "chat_v2"]


def decode_frame(data: bytes) -> tuple[str, bytes]:
    """Unpack [1 byte len][username][voice data] -> (username, voice_data)."""
    name_len = data[0]
    username = data[1 : 1 + name_len].decode()
    voice_data = data[1 + name_len :]
    return username, voice_data


def encode_v2_frame(username: str, voice_data: bytes) -> bytes:
    name_bytes = username.encode()
    return bytes([len(name_bytes)]) + name_bytes + voice_data


async def send_voice(ws, username: str, voice_byte: int, protocol: str) -> None:
    while True:
        burst_len = random.randint(2, 12)
        raw_voice = bytes([voice_byte] * burst_len)

        if protocol == "chat_v1":
            await ws.send(raw_voice)
        elif protocol == "chat_v2":
            await ws.send(encode_v2_frame(username, raw_voice))

        await asyncio.sleep(random.uniform(0.05, 0.2))

        if random.random() < 0.3:
            await asyncio.sleep(random.uniform(0.3, 1.0))


async def receive_voice(ws) -> None:
    async for message in ws:
        if isinstance(message, bytes):
            username, voice_data = decode_frame(message)
            ts = time.strftime("%H:%M:%S")
            print(f"{ts} voice from [{username}]: {voice_data}")


async def main() -> None:
    username = input("Enter your username: ").strip()
    voice_byte = int(input("Enter your voice byte (0-255): ").strip())

    uri = f"{SERVER}?username={username}"

    async with websockets.connect(uri, subprotocols=PROTOCOLS) as ws:
        chosen = ws.subprotocol
        print(f"Negotiated protocol: {chosen}\n")

        if not chosen:
            print("Server rejected all protocols.")
            return

        await asyncio.gather(
            send_voice(ws, username, voice_byte, chosen),
            receive_voice(ws),
        )


if __name__ == "__main__":
    asyncio.run(main())
