import time
import uuid
import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
STREAM = "demo_stream"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def produce(n=10, interval=1.0):
    for i in range(n):
        evt = {
            "id": str(uuid.uuid4()),
            "seq": str(i),
            "payload": f"message-{i}"
        }
        msg_id = r.xadd(STREAM, evt)
        print(f"Produced {msg_id} -> {evt}")
        time.sleep(interval)

if __name__ == "__main__":
    produce(n=20, interval=0.5)