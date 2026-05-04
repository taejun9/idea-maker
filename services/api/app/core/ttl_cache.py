from collections.abc import Callable, Hashable
from dataclasses import dataclass
from threading import Lock
from time import monotonic


@dataclass(frozen=True)
class TtlCacheEntry[T]:
    value: T
    expires_at: float


class TtlCache[T]:
    """Small in-process TTL cache shared by PLAN-0034 AI and source-index paths."""

    def __init__(
        self,
        *,
        ttl_seconds: float,
        max_entries: int,
        timer: Callable[[], float] = monotonic,
    ) -> None:
        self.ttl_seconds = max(0.0, ttl_seconds)
        self.max_entries = max(0, max_entries)
        self.timer = timer
        self._entries: dict[Hashable, TtlCacheEntry[T]] = {}
        self._lock = Lock()

    def get(self, key: Hashable) -> T | None:
        if self.ttl_seconds <= 0 or self.max_entries <= 0:
            return None

        now = self.timer()
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if entry.expires_at <= now:
                self._entries.pop(key, None)
                return None
            return entry.value

    def set(self, key: Hashable, value: T) -> None:
        if self.ttl_seconds <= 0 or self.max_entries <= 0:
            return

        with self._lock:
            if len(self._entries) >= self.max_entries and key not in self._entries:
                oldest_key = min(
                    self._entries,
                    key=lambda stored_key: self._entries[stored_key].expires_at,
                )
                self._entries.pop(oldest_key, None)
            self._entries[key] = TtlCacheEntry(
                value=value,
                expires_at=self.timer() + self.ttl_seconds,
            )

    def get_or_set(
        self,
        key: Hashable,
        factory: Callable[[], T],
        *,
        cacheable: Callable[[T], bool] | None = None,
    ) -> T:
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value

        value = factory()
        if cacheable is None or cacheable(value):
            self.set(key, value)
        return value

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
