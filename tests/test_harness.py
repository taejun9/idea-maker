import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_agents_is_a_short_map() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "Read First" in text
    assert len(text.splitlines()) <= 180


def test_runtime_task_kernel_exists() -> None:
    text = (ROOT / "RTK.md").read_text(encoding="utf-8")

    assert "Last reviewed:" in text
    assert "scripts/agent-task.sh ci" in text


def test_exec_plan_guard_passes_current_tree() -> None:
    subprocess.run(
        [sys.executable, "tools/exec_plan_guard.py"],
        cwd=ROOT,
        check=True,
    )
