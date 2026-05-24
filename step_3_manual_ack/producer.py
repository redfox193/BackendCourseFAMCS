import time
from datetime import datetime

import pika


EXCHANGE_NAME = "demo_direct"
ROUTING_KEY = "info"


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="direct",
        durable=True,
    )

    while True:
        message = f"Hello World at {datetime.now().strftime('%H:%M:%S')}!"

        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=ROUTING_KEY,
            body=message,
        )

        print(f"[x] Sent '{ROUTING_KEY}':'{message}'")
        time.sleep(1)


if __name__ == "__main__":
    main()