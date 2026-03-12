import os
import time
import requests


RANDOM_SERVICE_HOST = os.getenv('RANDOM_SERVICE_URL', 'http://localhost:8000')


def main():
    while True:
        try:
            response = requests.get(RANDOM_SERVICE_HOST + '/random')
            response.raise_for_status()
            data = response.json()
            print(data.get("number"))
        except Exception as exc:
            print(f"request error: {exc}")
        time.sleep(1)


if __name__ == "__main__":
    main()
