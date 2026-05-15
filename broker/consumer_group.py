import time
import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
STREAM = "demo_stream"
GROUP = "demo_group"
CONSUMER = "consumer-2"

def process_message(msg_id, fields):
    print(f"[{CONSUMER}] Processing {msg_id}: {fields}")
    time.sleep(0.1)
    raise RuntimeError(f"Error processing {msg_id}")

def main():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    while True:
        try:
            res = r.xreadgroup(GROUP, CONSUMER, {STREAM: ">"}, count=1, block=2000)
        except redis.exceptions.RedisError as e:
            print("Redis error:", e)
            time.sleep(1)
            continue

        if not res:
            continue

        for stream_name, messages in res:
            for msg_id, fields in messages:
                try:
                    process_message(msg_id, fields)
                    r.xack(STREAM, GROUP, msg_id)
                except Exception as e:
                    print(f"Error processing {msg_id}: {e}")

    print("Consumer shutting down")

if __name__ == "__main__":
    main()