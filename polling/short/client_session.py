import time

import httpx

BASE_URL = 'http://127.0.0.1:8000'
POLL_INTERVAL = 1.0


def main() -> None:
    limits = httpx.Limits(
        keepalive_expiry=2.0
    )

    with httpx.Client(limits=limits) as client:
        resp = client.post(f'{BASE_URL}/jobs')
        resp.raise_for_status()
        job_id = resp.json()['job_id']
        print(f'Job created: {job_id}\n')

        while True:
            resp = client.get(f'{BASE_URL}/jobs/{job_id}')
            resp.raise_for_status()
            data = resp.json()

            print(f'[{data["status"].upper():>7}] progress={data["progress"]:>3}%')

            if data['status'] == 'done':
                print(f'\nFinal result: {data["result"]}')
                break

            time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    main()
