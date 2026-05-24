import os
import sys
import time

import pika


QUEUE_NAME = "task_queue"


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
    )

    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        message = body.decode("utf-8")
        worker_name = os.getpid()

        print(f"[x] Worker {worker_name} received: {message}")

        dots_count = message.count(".")
        time.sleep(dots_count)

        print(f"[x] Worker {worker_name} done: {message}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"[x] Worker {worker_name} acked: {message}")

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