import os
from collections.abc import Mapping


def database_url(environment: Mapping[str, str] = os.environ) -> str | None:
    configured_url = environment.get("DATABASE_URL", "").strip()
    return configured_url or None
