from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_agents_is_a_short_map() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "Read First" in text
    assert len(text.splitlines()) <= 180

