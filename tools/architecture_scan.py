"""Pattern-based architecture scan.

This intentionally starts simple. Add rules to lint-rules/architecture_rules.yml
when repeated review feedback should become mechanical enforcement.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RULES = [
    {
        "id": "frontend-no-backend-internals",
        "base": "apps/web/src",
        "patterns": ["services/api"],
    },
    {
        "id": "component-no-fetch",
        "base": "apps/web/src/components",
        "patterns": ["fetch("],
    },
    {
        "id": "route-no-db-driver",
        "base": "services/api/app/routes",
        "patterns": ["import sqlite3", "import psycopg", "from sqlalchemy"],
    },
    {
        "id": "no-secret-ish-values",
        "base": ".",
        "patterns": ["sk-live-", "ghp_", "xoxb-"],
        "ignore_parts": {
            ".git",
            ".worktrees",
            "node_modules",
            ".venv",
            "__pycache__",
            "lint-rules",
        },
        "ignore_paths": {"tools/architecture_scan.py"},
    },
]

TEXT_EXTENSIONS = {
    ".md",
    ".py",
    ".ts",
    ".tsx",
    ".vue",
    ".js",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".sh",
}


def iter_files(base: Path, ignore_parts: set[str], ignore_paths: set[str]) -> list[Path]:
    if not base.exists():
        return []
    if base.is_file():
        return [base]
    return [
        path
        for path in base.rglob("*")
        if path.is_file()
        and path.suffix in TEXT_EXTENSIONS
        and not (set(path.parts) & ignore_parts)
        and str(path.relative_to(ROOT)) not in ignore_paths
    ]


def main() -> int:
    failures: list[str] = []
    for rule in RULES:
        ignore_parts = set(rule.get("ignore_parts", set()))
        ignore_paths = set(rule.get("ignore_paths", set()))
        for path in iter_files(ROOT / rule["base"], ignore_parts, ignore_paths):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in rule["patterns"]:
                if pattern in text:
                    rel = path.relative_to(ROOT)
                    failures.append(f"{rule['id']}: {rel} contains {pattern!r}")

    if failures:
        print("Architecture violations:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("architecture_scan: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
