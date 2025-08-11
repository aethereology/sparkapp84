import os, json
from typing import Optional
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
SOCKET_TIMEOUT = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
DEFAULT_RECEIPT_TTL = int(os.getenv("RECEIPT_TTL_SEC", str(30*24*3600)))
DEFAULT_STATEMENT_TTL = int(os.getenv("STATEMENT_TTL_SEC", str(90*24*3600)))
_pool = redis.ConnectionPool.from_url(REDIS_URL, max_connections=REDIS_MAX_CONNECTIONS, socket_timeout=SOCKET_TIMEOUT)
r = redis.Redis(connection_pool=_pool)

def _bkey(kind: str, key: str) -> bytes: return f"spark:{kind}:{key}".encode()
def cache_stats() -> dict:
    try: info = r.info(); return {"used_memory": info.get("used_memory_human"), "hits": info.get("keyspace_hits"), "misses": info.get("keyspace_misses")}
    except Exception: return {"status": "redis_unavailable"}

def get_cached_receipt_pdf(donation_id: str) -> Optional[bytes]:
    try: return r.get(_bkey("receipt", donation_id))
    except Exception: return None

def cache_receipt_pdf(donation_id: str, pdf: bytes, ttl: int = DEFAULT_RECEIPT_TTL):
    try: r.setex(_bkey("receipt", donation_id), ttl, pdf)
    except Exception: pass

def get_cached_statement_pdf(donor_id: str, year: int) -> Optional[bytes]:
    try: return r.get(_bkey("statement", f"{donor_id}:{year}"))
    except Exception: return None

def cache_statement_pdf(donor_id: str, year: int, pdf: bytes, ttl: int = DEFAULT_STATEMENT_TTL):
    try: r.setex(_bkey("statement", f"{donor_id}:{year}"), ttl, pdf)
    except Exception: pass
