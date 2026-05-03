"""Quality score smoke check."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    path = ROOT / "docs/quality/quality-score.md"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"Overall:\s+(\d+)\s*/\s*100", text)
    if not match:
        print("docs/quality/quality-score.md must include 'Overall: N / 100'")
        return 1
    score = int(match.group(1))
    if score < 60:
        print(f"Quality score too low for feature work: {score}")
        return 1
    print(f"quality_score: ok ({score}/100)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
