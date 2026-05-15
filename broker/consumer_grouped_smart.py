import time
import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
STREAM = "demo_stream"
GROUP = "demo_group"
CONSUMER = "consumer-3"

# Rehab params
RECLAIM_IDLE_MS = 30_000
RECLAIM_BATCH_SIZE = 10
RECLAIM_INTERVAL_SEC = 5
MAX_RETRIES = 1
DLQ_STREAM = STREAM + "_dlq"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def process_message(msg_id, fields):
    print(f"[{CONSUMER}] Processing {msg_id}: {fields}")
    time.sleep(0.1)
    raise RuntimeError(f"Error processing {msg_id}")

def move_to_dlq(msg_id, fields):
    r.xadd(DLQ_STREAM, {**fields, "_orig_id": msg_id})
    r.xack(STREAM, GROUP, msg_id)
    print(f"[{CONSUMER}] Moved {msg_id} to DLQ")

def claim_and_process(ids, id_to_attempts):
    try:
        claimed = r.xclaim(STREAM, GROUP, CONSUMER, min_idle_time=RECLAIM_IDLE_MS, message_ids=ids)
    except redis.exceptions.RedisError as e:
        print("XCLAIM error:", e)
        return

    for msg_id, fields in claimed:
        if id_to_attempts[msg_id] > MAX_RETRIES:
            move_to_dlq(msg_id, fields)
            continue

        try:
            process_message(msg_id, fields)
            r.xack(STREAM, GROUP, msg_id)
        except Exception as e:
            print(f"Error processing claimed {msg_id}: {e}")
            pass

def rehab_cycle():
    # [id, consumer, idle, deliveries]
    pendings = r.xpending_range(STREAM, GROUP, min='-', max='+', count=RECLAIM_BATCH_SIZE)

    ids_to_claim = []
    id_to_attempts = {}
    for item in pendings:
        msg_id = item['message_id']
        idle = item['time_since_delivered']
        attempts = item['times_delivered']

        if idle >= RECLAIM_IDLE_MS:
            ids_to_claim.append(msg_id)
            id_to_attempts[msg_id] = attempts

    if ids_to_claim:
        claim_and_process(ids_to_claim, id_to_attempts)

def main():
    last_reclaim = time.time()

    while True:
        now = time.time()
        if now - last_reclaim > RECLAIM_INTERVAL_SEC:
            rehab_cycle()
            last_reclaim = now

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