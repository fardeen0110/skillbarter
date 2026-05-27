from __future__ import annotations

import threading
from collections import defaultdict, deque
from time import time

from fastapi import HTTPException, status

from ..config import get_settings

settings = get_settings()


class SlidingWindowRateLimiter:
    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, *, limit: int, window_seconds: int) -> None:
        now = time()
        window_start = now - window_seconds

        with self._lock:
            events = self._events[key]
            while events and events[0] < window_start:
                events.popleft()
            if len(events) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again shortly.",
                )
            events.append(now)


request_rate_limiter = SlidingWindowRateLimiter()
websocket_rate_limiter = SlidingWindowRateLimiter()


def request_limit_for(identifier: str) -> None:
    request_rate_limiter.check(
        identifier,
        limit=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )


def websocket_limit_for(identifier: str) -> None:
    websocket_rate_limiter.check(
        identifier,
        limit=settings.websocket_message_limit,
        window_seconds=settings.websocket_message_window_seconds,
    )
