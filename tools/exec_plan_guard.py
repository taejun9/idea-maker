"""Validate execution plan placement and required sections."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_DIR = ROOT / "docs/exec-plans/active"
COMPLETED_DIR = ROOT / "docs/exec-plans/completed"
PLAN_FILE_RE = re.compile(r"^plan-(?P<num>[0-9]{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")

ACTIVE_REQUIRED_SECTIONS = [
    "## Goal",
    "## Non-Goals",
    "## Constraints",
    "## Task Breakdown",
    "## Verification",
    "## Rollback Strategy",
    "## Decision Log",
    "## Definition of Done",
]

COMPLETED_REQUIRED_SECTIONS = [
    "## Outcome",
    "## Verification",
    "## Follow-Up Cleanup",
]


def plan_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.md") if path.is_file())


def has_line(text: str, prefix: str, expected_value: str | None = None) -> bool:
    for line in text.splitlines():
        if not line.startswith(prefix):
            continue
        if expected_value is None:
            return bool(line.removeprefix(prefix).strip())
        return line.removeprefix(prefix).strip().lower() == expected_value
    return False


def validate_filename(path: Path, failures: list[str]) -> str | None:
    match = PLAN_FILE_RE.match(path.name)
    if match is None:
        failures.append(f"{path.relative_to(ROOT)}: filename must be plan-NNNN-<task>.md")
        return None
    return match.group("num")


def validate_plan(path: Path, expected_status: str, failures: list[str]) -> None:
    num = validate_filename(path, failures)
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT)

    if num is not None and f"# PLAN-{num}" not in text:
        failures.append(f"{rel}: title must include PLAN-{num}")
    if not has_line(text, "Status:", expected_status):
        failures.append(f"{rel}: Status must be {expected_status}")
    if not has_line(text, "Owner:"):
        failures.append(f"{rel}: missing Owner metadata")

    if expected_status == "active":
        if not has_line(text, "Last updated:"):
            failures.append(f"{rel}: missing Last updated metadata")
        if not has_line(text, "Related docs:"):
            failures.append(f"{rel}: missing Related docs metadata")
        if not has_line(text, "Roles:"):
            failures.append(f"{rel}: missing Roles metadata")
        for section in ACTIVE_REQUIRED_SECTIONS:
            if section not in text:
                failures.append(f"{rel}: missing {section}")
    else:
        for section in COMPLETED_REQUIRED_SECTIONS:
            if section not in text:
                failures.append(f"{rel}: missing {section}")


def main() -> int:
    failures: list[str] = []
    if not ACTIVE_DIR.exists():
        failures.append("docs/exec-plans/active directory is missing")
    if not (ACTIVE_DIR / ".gitkeep").exists():
        failures.append("docs/exec-plans/active/.gitkeep is missing")
    if not COMPLETED_DIR.exists():
        failures.append("docs/exec-plans/completed directory is missing")

    active_plans = plan_files(ACTIVE_DIR)
    completed_plans = plan_files(COMPLETED_DIR)

    for path in active_plans:
        validate_plan(path, "active", failures)
    for path in completed_plans:
        validate_plan(path, "completed", failures)

    if failures:
        print("Execution plan guard failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"exec_plan_guard: ok (active={len(active_plans)}, completed={len(completed_plans)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
