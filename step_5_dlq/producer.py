import uuid
import pika


QUEUE_NAME = "task_queue"


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    messages = [
        "task-1 .",
        "task-2 ..",
        "task-3 ...",
        "task-4 .",
        "task-5 ....",
        "task-6 ..",
    ]

    for message in messages:
        message_id = str(uuid.uuid4())

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
                message_id=message_id,
                headers={
                    "x-retry-count": 0,
                },
            ),
        )
        print(f"[x] Sent id={message_id} body='{message}'")

    connection.close()


if __name__ == "__main__":
    main()