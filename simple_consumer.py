import redis
import sys
import json

REDIS_HOST = "localhost"
REDIS_PORT = 6379
STREAM_NAME = "somestream"

def consume():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    try:
        entries = r.xread({STREAM_NAME: "$"}, block=0, count=1)
    except redis.exceptions.RedisError as e:
        print(f"Redis error: {e}", file=sys.stderr)
        sys.exit(2)

    if not entries:
        print("No entries returned.")
        return

    stream, msgs = entries[0]
    msg_id, fields = msgs[0]
    print(json.dumps({"id": msg_id, "stream": stream, "fields": fields}, ensure_ascii=False))

while True:
    consume()