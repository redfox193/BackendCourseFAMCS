import argparse
import os

import uvicorn


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run demo FastAPI service")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--postgresql", required=True, help="PostgreSQL DSN")
    parser.add_argument(
        "--currency-api-base-url",
        required=True,
        help="Base URL for external currency API (mockserver in tests)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    os.environ["DATABASE_URL"] = args.postgresql
    os.environ["CURRENCY_API_BASE_URL"] = args.currency_api_base_url
    from app.main import app

    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
