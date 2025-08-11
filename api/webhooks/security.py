import os, hmac, hashlib, base64, json, time
from typing import Dict, Optional
from fastapi import HTTPException
from cache.redis_cache import r as redis_client

SQUARE_SIGNATURE_KEY = os.getenv("SQUARE_WEBHOOK_SIGNATURE_KEY", "")
SQUARE_NOTIFICATION_URL = os.getenv("SQUARE_NOTIFICATION_URL", "")
IDEMPOTENCY_KEY_TTL = int(os.getenv("IDEMPOTENCY_KEY_TTL", "86400"))
WEBHOOK_RATE_LIMIT_PER_MINUTE = int(os.getenv("WEBHOOK_RATE_LIMIT_PER_MINUTE", "100"))
TIMESTAMP_TOLERANCE = int(os.getenv("WEBHOOK_TIMESTAMP_TOLERANCE", "300"))

def verify_square_webhook(raw_body: bytes, signature: str) -> bool:
    if not SQUARE_SIGNATURE_KEY or not SQUARE_NOTIFICATION_URL:
        return True
    mac = hmac.new(SQUARE_SIGNATURE_KEY.encode("utf-8"),
                   (SQUARE_NOTIFICATION_URL + raw_body.decode("utf-8")).encode("utf-8"),
                   hashlib.sha256).digest()
    expected = base64.b64encode(mac).decode("utf-8")
    return hmac.compare_digest(expected, signature or "")

def check_timestamp(ts_header: Optional[str]) -> bool:
    if not ts_header: return True
    try:
        ts = int(ts_header)
        return abs(int(time.time()) - ts) <= TIMESTAMP_TOLERANCE
    except Exception: return False

def rate_limit(provider: str, source: str):
    key = f"rl:{provider}:{source}:{int(time.time()//60)}"
    try:
        cnt = redis_client.incr(key)
        if cnt == 1: redis_client.expire(key, 60)
        if cnt > WEBHOOK_RATE_LIMIT_PER_MINUTE:
            raise HTTPException(status_code=429, detail="Too Many Requests")
    except HTTPException: raise
    except Exception: pass

def idem_check(provider: str, event_id: str) -> Optional[Dict]:
    key = f"idem:{provider}:{event_id}"
    try:
        data = redis_client.get(key)
        if data:
            try: return json.loads(data.decode("utf-8"))
            except Exception: return {"cached": True}
        return None
    except Exception: return None

def idem_store(provider: str, event_id: str, result: Dict):
    key = f"idem:{provider}:{event_id}"
    try: redis_client.setex(key, IDEMPOTENCY_KEY_TTL, json.dumps(result))
    except Exception: pass

def process_lock(provider: str, event_id: str, ttl: int = 30) -> bool:
    key = f"lock:{provider}:{event_id}"
    try:
        ok = redis_client.set(key, "1", nx=True, ex=ttl)
        return bool(ok)
    except Exception: return True
