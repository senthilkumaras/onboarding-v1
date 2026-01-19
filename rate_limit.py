import time
import hashlib

WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 12  # tweak for demo

_bucket = {}  # {user_key: [timestamps]}


def make_user_key(session_id: str, user_agent: str) -> str:
    raw = f"{session_id}|{user_agent}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def allow(user_key: str) -> bool:
    now = time.time()
    ts = _bucket.get(user_key, [])
    ts = [t for t in ts if now - t < WINDOW_SECONDS]
    if len(ts) >= MAX_REQUESTS_PER_WINDOW:
        _bucket[user_key] = ts
        return False
    ts.append(now)
    _bucket[user_key] = ts
    return True
