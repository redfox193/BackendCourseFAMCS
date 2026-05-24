import os
import sys
import pika


DLQ_NAME = "task_dlq"


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    channel.queue_declare(queue=DLQ_NAME, durable=True)

    def callback(ch, method, properties, body):
        headers = properties.headers or {}
        print(
            f"[DLQ] id={properties.message_id} "
            f"retry={headers.get('x-retry-count')} "
            f"error={headers.get('x-last-error')} "
            f"body='{body.decode()}'"
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=DLQ_NAME,
        on_message_callback=callback,
        auto_ack=False,
    )

    print("[*] Waiting for dead letters. To exit press CTRL+C")
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