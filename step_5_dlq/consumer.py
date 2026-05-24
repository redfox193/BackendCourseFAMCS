import os
import sys
import time
import random

import pika


QUEUE_NAME = "task_queue"
DLX_NAME = "task_dlx"
DLQ_NAME = "task_dlq"
DLQ_ROUTING_KEY = "dead"
MAX_RETRIES = 2


def process_message(message: str):
    time.sleep(message.count("."))
    #if random.random() < 0.5:
    raise RuntimeError("Random processing error")


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange=DLX_NAME,
        exchange_type="direct",
        durable=True,
    )

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_declare(queue=DLQ_NAME, durable=True)
    channel.queue_bind(
        exchange=DLX_NAME,
        queue=DLQ_NAME,
        routing_key=DLQ_ROUTING_KEY,
    )

    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        worker_name = os.getpid()
        message = body.decode("utf-8")

        headers = properties.headers or {}
        retry_count = int(headers.get("x-retry-count", 0))
        message_id = properties.message_id or "unknown"

        print(
            f"[x] Worker {worker_name} received "
            f"id={message_id} retry={retry_count} body='{message}'"
        )

        try:
            process_message(message)
            print(f"[x] Worker {worker_name} success id={message_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as exc:
            print(
                f"[!] Worker {worker_name} failed "
                f"id={message_id} retry={retry_count} error='{exc}'"
            )

            next_retry = retry_count + 1

            if retry_count < MAX_RETRIES:
                ch.basic_publish(
                    exchange="",
                    routing_key=QUEUE_NAME,
                    body=body,
                    properties=pika.BasicProperties(
                        delivery_mode=pika.DeliveryMode.Persistent,
                        message_id=message_id,
                        headers={
                            "x-retry-count": next_retry,
                            "x-last-error": str(exc),
                        },
                    ),
                )
                print(
                    f"[>] Requeued manually "
                    f"id={message_id} next_retry={next_retry}"
                )
            else:
                ch.basic_publish(
                    exchange=DLX_NAME,
                    routing_key=DLQ_ROUTING_KEY,
                    body=body,
                    properties=pika.BasicProperties(
                        delivery_mode=pika.DeliveryMode.Persistent,
                        message_id=message_id,
                        headers={
                            "x-retry-count": retry_count,
                            "x-last-error": str(exc),
                            "x-original-queue": QUEUE_NAME,
                        },
                    ),
                )
                print(
                    f"[>] Sent to DLQ "
                    f"id={message_id} retries_exhausted={retry_count}"
                )

            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=False,
    )

    print("[*] Waiting for messages. To exit press CTRL+C")
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