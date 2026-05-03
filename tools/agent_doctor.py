"""Local doctor command for Codex."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    print(f"workspace: {ROOT}")
    for command in ["python", "python3", "git", "docker"]:
        found = shutil.which(command)
        print(f"{command}: {found or 'missing'}")
    print("node:", shutil.which("node") or "missing", "(Docker runtime uses Node 22)")
    print("npm:", shutil.which("npm") or "missing")
    print("agent_doctor: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
