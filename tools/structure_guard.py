"""Repository structure checks for Codex harness."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "AGENTS.md",
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
    "docs/exec-plans/README.md",
    "docs/exec-plans/tech-debt-tracker.md",
    "docs/references/README.md",
    "docs/references/codex-extensions.md",
    "docs/generated/db-schema.md",
    "scripts/agent-task.sh",
    "tools/architecture_scan.py",
    "lint-rules/architecture_rules.yml",
    ".github/workflows/ci.yml",
]


def main() -> int:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    if missing:
        print("Missing required harness paths:")
        for path in missing:
            print(f"- {path}")
        return 1

    agents_lines = (ROOT / "AGENTS.md").read_text(encoding="utf-8").splitlines()
    if len(agents_lines) > 180:
        print(f"AGENTS.md is too long: {len(agents_lines)} lines; max is 180")
        return 1

    print("structure_guard: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
