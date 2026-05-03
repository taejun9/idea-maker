"""Check required docs include review metadata."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DOCS = [
    "docs/architecture/README.md",
    "docs/architecture/backend.md",
    "docs/architecture/frontend.md",
    "docs/quality/quality-score.md",
    "docs/quality/review-rubric.md",
    "docs/operations/reliability.md",
    "docs/operations/security.md",
    "docs/observability/README.md",
    "docs/HARNESS_SYSTEM.md",
    "docs/design-docs/index.md",
    "docs/design-docs/core-beliefs.md",
    "docs/product-specs/index.md",
    "docs/team/roster.md",
    "docs/exec-plans/README.md",
    "docs/exec-plans/tech-debt-tracker.md",
    "docs/references/README.md",
    "docs/references/codex-git-workflow.md",
    "docs/references/codex-extensions.md",
    "docs/generated/db-schema.md",
]


def main() -> int:
    failures: list[str] = []
    for rel_path in REQUIRED_DOCS:
        path = ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        if "Last reviewed:" not in text:
            failures.append(rel_path)

    if failures:
        print("Docs missing Last reviewed metadata:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("docs_freshness: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
