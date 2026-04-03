import httpx
import threading
import time

BASE_URL = 'http://127.0.0.1:8000'


def sender(author: str) -> None:
    with httpx.Client() as client:
        while True:
            text = input()
            if text.strip():
                client.post(f'{BASE_URL}/message', json={'author': author, 'text': text})


def receiver(author: str) -> None:
    since_id = -1
    with httpx.Client(timeout=40.0) as client:  # > server timeout
        while True:
            try:
                resp = client.get(f'{BASE_URL}/poll', params={'since_id': since_id, 'timeout': 30})
                resp.raise_for_status()
                data = resp.json()

                for msg in data['messages']:
                    if msg['author'] != author:
                        print(f'\n[{msg['author']}]: {msg['text']}')
                    since_id = max(since_id, msg['id'])

            except httpx.RequestError as e:
                print(f'Connection error: {e}, retrying...')
                time.sleep(1)


if __name__ == '__main__':
    name = input('Your name: ').strip()

    t = threading.Thread(target=receiver, args=(name,), daemon=True)
    t.start()

    sender(name)
