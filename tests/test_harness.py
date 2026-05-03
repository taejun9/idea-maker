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
    assert "<작업자명>: <작업내용>" in text
    assert "<작업자명>: <보고내용>" in text


def test_exec_plan_guard_passes_current_tree() -> None:
    subprocess.run(
        [sys.executable, "tools/exec_plan_guard.py"],
        cwd=ROOT,
        check=True,
    )


def test_agent_task_reports_start_with_worker_prefix() -> None:
    start = subprocess.run(
        [
            "scripts/agent-task.sh",
            "start-report",
            "plan-9999-example",
            "Do the work",
            "기록관",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    finish = subprocess.run(
        [
            "scripts/agent-task.sh",
            "finish-report",
            "plan-9999-example",
            "Done",
            "기록관",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert start.stdout.splitlines()[0] == "기록관: Do the work"
    assert finish.stdout.splitlines()[0] == "기록관: Done"
