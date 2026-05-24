import time

import pika
from datetime import datetime


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    channel.queue_declare(
        queue="hello",
        durable=True,
    )

    while True:
        message = f"Hello World at {datetime.now().strftime('%H:%M:%S')}!"

        channel.basic_publish(
            exchange="",
            routing_key="hello",
            body=message,
        )

        print(f"[x] Sent: {message}")
        time.sleep(1)


if __name__ == "__main__":
    main()