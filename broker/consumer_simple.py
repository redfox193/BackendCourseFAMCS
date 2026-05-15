import time
import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
STREAM = "demo_stream"
CONSUMER = "simple"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
running = True

def main():
    last_id = "0"
    while running:
        try:
            entries = r.xread({STREAM: last_id}, block=0, count=1)
        except redis.exceptions.RedisError as e:
            print("Redis error:", e)
            time.sleep(1)
            continue

        if not entries:
            continue

        stream_name, messages = entries[0]
        msg_id, fields = messages[0]
        last_id = msg_id
        print(f"[{CONSUMER}] Got {msg_id}: {fields}")

    print("Simple consumer shutting down")

if __name__ == "__main__":
    main()