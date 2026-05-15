import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
STREAM = "demo_stream"
GROUP = "demo_group"
DLQ_STREAM = STREAM + "_dlq"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def delete_stream(key):
    try:
        r.delete(key)
        print(f"Deleted key '{key}' (if existed).")
    except redis.exceptions.RedisError as e:
        print(f"Error deleting '{key}': {e}")

def ensure_group():
    r.xgroup_create(STREAM, GROUP, id="0", mkstream=True)
    print(f"Consumer group '{GROUP}' created on stream '{STREAM}'")

def main():
    delete_stream(STREAM)
    delete_stream(DLQ_STREAM)

    ensure_group()

if __name__ == "__main__":
    main()