"""Small local markdown link checker for repository-relative links."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def should_skip(target: str) -> bool:
    return (
        target.startswith("http://")
        or target.startswith("https://")
        or target.startswith("mailto:")
        or target.startswith("#")
    )


def normalize(source: Path, target: str) -> Path:
    clean = target.split("#", 1)[0]
    if not clean:
        return source
    return (source.parent / clean).resolve()


def main() -> int:
    failures: list[str] = []
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1)
            if should_skip(target):
                continue
            resolved = normalize(path, target)
            if not resolved.exists():
                failures.append(f"{path.relative_to(ROOT)} -> {target}")

    if failures:
        print("Broken markdown links:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("link_check: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

