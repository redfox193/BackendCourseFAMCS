import httpx
import time

BASE_URL = 'http://127.0.0.1:8000'


def run_bot() -> None:
    since_id = -1

    with httpx.Client(timeout=40.0) as client:
        resp = client.get(f'{BASE_URL}/poll', params={'since_id': since_id, 'timeout': 0.01})
        data = resp.json()

        if data['messages']:
            since_id = max(m['id'] for m in data['messages'])

        while True:
            try:
                resp = client.get(
                    f'{BASE_URL}/poll',
                    params={'since_id': since_id, 'timeout': 30.0},
                )
                resp.raise_for_status()
                data = resp.json()

                for msg in data['messages']:
                    since_id = max(since_id, msg['id'])

                    if msg['author'] == 'echo_bot':
                        continue

                    print(f'[echo_bot] got: "{msg['text']}" from {msg['author']}')
                    client.post(f'{BASE_URL}/message', json={'author': 'echo_bot', 'text': msg['text']})

            except httpx.RequestError as e:
                print(f'[echo_bot] connection error: {e}, retrying in 2s...')
                time.sleep(2)


if __name__ == '__main__':
    run_bot()
