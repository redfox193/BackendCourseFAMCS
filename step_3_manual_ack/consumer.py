import os
import sys
import time

import pika


EXCHANGE_NAME = "demo_direct"
QUEUE_NAME = "hello"
BINDING_KEY = "info"


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

    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
    )

    channel.queue_bind(
        exchange=EXCHANGE_NAME,
        queue=QUEUE_NAME,
        routing_key=BINDING_KEY,
    )

    channel.basic_qos(prefetch_count=5)

    def callback(ch, method, properties, body):
        time.sleep(1)
        print(
            f"[x] Received from exchange='{method.exchange}' "
            f"routing_key='{method.routing_key}': "
            f"{body.decode('utf-8')}"
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
    )

    print(
        f"[*] Waiting for messages in queue='{QUEUE_NAME}' "
        f"bound to exchange='{EXCHANGE_NAME}' with key='{BINDING_KEY}'"
    )
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)