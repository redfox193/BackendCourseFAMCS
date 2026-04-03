import httpx

URL = "http://127.0.0.1:8000/events"


def main() -> None:
    with httpx.Client(timeout=None) as client:
        with client.stream("GET", URL) as resp:
            print(f"Connected, status={resp.status_code}\n")
            for line in resp.iter_raw():
                print(line.decode("utf-8"))


if __name__ == "__main__":
    main()
