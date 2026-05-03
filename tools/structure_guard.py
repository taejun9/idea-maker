"""Repository structure checks for Codex harness."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE_RE = re.compile(r"^@(?P<target>[A-Za-z0-9_./-]+\.md)\s*$")
READ_FIRST_PATH_RE = re.compile(r"`(?P<target>[^`]+)`")

REQUIRED_PATHS = [
    "AGENTS.md",
    "RTK.md",
    "docs/architecture/README.md",
    "docs/architecture/backend.md",
    "docs/architecture/frontend.md",
    "docs/quality/quality-score.md",
    "docs/quality/review-rubric.md",
    "docs/operations/reliability.md",
    "docs/operations/security.md",
    "docs/observability/README.md",
    "docs/design-docs/index.md",
    "docs/design-docs/core-beliefs.md",
    "docs/product-specs/index.md",
    "docs/exec-plans/active",
    "docs/exec-plans/active/.gitkeep",
    "docs/exec-plans/completed",
    "docs/exec-plans/README.md",
    "docs/exec-plans/tech-debt-tracker.md",
    "docs/references/README.md",
    "docs/references/codex-extensions.md",
    "docs/generated/db-schema.md",
    "scripts/agent-task.sh",
    "tools/architecture_scan.py",
    "tools/exec_plan_guard.py",
    "lint-rules/architecture_rules.yml",
    ".github/workflows/ci.yml",
]


def read_first_paths(agents_text: str) -> list[str]:
    paths: list[str] = []
    in_read_first = False
    for line in agents_text.splitlines():
        if line.startswith("## "):
            in_read_first = line == "## Read First"
            continue
        if not in_read_first:
            continue
        paths.extend(match.group("target") for match in READ_FIRST_PATH_RE.finditer(line))
    return paths


def include_paths(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [
        match.group("target")
        for line in text.splitlines()
        if (match := INCLUDE_RE.match(line.strip()))
    ]


def main() -> int:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    if missing:
        print("Missing required harness paths:")
        for path in missing:
            print(f"- {path}")
        return 1

    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    agents_lines = agents_text.splitlines()
    if len(agents_lines) > 180:
        print(f"AGENTS.md is too long: {len(agents_lines)} lines; max is 180")
        return 1

    broken_refs: list[str] = []
    for rel_path in read_first_paths(agents_text):
        if not (ROOT / rel_path).exists():
            broken_refs.append(f"AGENTS.md Read First -> {rel_path}")
    for source in ["AGENTS.md", "RTK.md"]:
        for rel_path in include_paths(ROOT / source):
            if not (ROOT / rel_path).exists():
                broken_refs.append(f"{source} include -> {rel_path}")
    if broken_refs:
        print("Broken harness references:")
        for ref in broken_refs:
            print(f"- {ref}")
        return 1

    print("structure_guard: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
