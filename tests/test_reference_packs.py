from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_fact_checker_uses_reference_pack() -> None:
    skill_path = ROOT / ".claude" / "skills" / "fact-checker" / "SKILL.md"
    pack_path = ROOT / "references" / "packs" / "fact-checker.md"

    skill_text = skill_path.read_text(encoding="utf-8")
    pack_text = pack_path.read_text(encoding="utf-8")

    assert "references/packs/fact-checker.md" in skill_text
    assert len(skill_text.splitlines()) <= 130
    assert "## Phase 3.5 — Source Laundering Detection" in pack_text
    assert "## Phase 3.3 — Similar-Statute Cross-Check" in pack_text
    assert "## Phase 4 — Claim Registry Output" in pack_text


def test_ingest_uses_reference_pack() -> None:
    skill_path = ROOT / ".claude" / "skills" / "ingest" / "SKILL.md"
    pack_path = ROOT / "references" / "packs" / "ingest.md"

    skill_text = skill_path.read_text(encoding="utf-8")
    pack_text = pack_path.read_text(encoding="utf-8")

    assert "references/packs/ingest.md" in skill_text
    assert len(skill_text.splitlines()) <= 125
    assert "## Step 2 — Markdown Conversion" in pack_text
    assert "## Step 3 — Grade Classification" in pack_text
    assert "## Step 4 — Frontmatter Generation" in pack_text
    assert "## Step 6 — Index Update" in pack_text


def test_onboard_uses_reference_pack() -> None:
    skill_path = ROOT / ".claude" / "skills" / "onboard" / "SKILL.md"
    pack_path = ROOT / "references" / "packs" / "onboard.md"

    skill_text = skill_path.read_text(encoding="utf-8")
    pack_text = pack_path.read_text(encoding="utf-8")

    assert "references/packs/onboard.md" in skill_text
    assert len(skill_text.splitlines()) <= 110
    assert "## Starter Templates" in pack_text
    assert "## Custom Interview" in pack_text
    assert "## user-config.json Schema" in pack_text
    assert "## Directory Initialization" in pack_text
