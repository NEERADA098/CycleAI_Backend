import time
from collections import defaultdict, deque
from fastapi import HTTPException, Request

WINDOW_SECONDS = 60
MAX_REQUESTS = 12
_hits = defaultdict(deque)


def chat_rate_limit(request: Request) -> None:
    forwarded = request.headers.get("x-forwarded-for", "")
    ip = forwarded.split(",")[0].strip() or (
        request.client.host if request.client else "unknown"
    )
    now = time.monotonic()
    hits = _hits[ip]
    while hits and now - hits[0] > WINDOW_SECONDS:
        hits.popleft()
    if len(hits) >= MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a minute.")
    hits.append(now)
