import os
from collections.abc import Mapping


def database_url(environment: Mapping[str, str] = os.environ) -> str | None:
    configured_url = environment.get("DATABASE_URL", "").strip()
    return configured_url or None


def ai_generation_cache_ttl_seconds(
    environment: Mapping[str, str] = os.environ,
) -> float:
    return max(0.0, float(environment.get("AI_GENERATION_CACHE_TTL_SECONDS", "600")))


def ai_generation_cache_max_entries(
    environment: Mapping[str, str] = os.environ,
) -> int:
    return max(0, int(environment.get("AI_GENERATION_CACHE_MAX_ENTRIES", "128")))


def source_index_cache_ttl_seconds(
    environment: Mapping[str, str] = os.environ,
) -> float:
    return max(0.0, float(environment.get("SOURCE_INDEX_CACHE_TTL_SECONDS", "300")))


def source_index_cache_max_entries(
    environment: Mapping[str, str] = os.environ,
) -> int:
    return max(0, int(environment.get("SOURCE_INDEX_CACHE_MAX_ENTRIES", "16")))
