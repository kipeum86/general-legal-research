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


def test_web_researcher_uses_reference_pack() -> None:
    skill_path = ROOT / ".claude" / "skills" / "web-researcher" / "SKILL.md"
    pack_path = ROOT / "references" / "packs" / "web-researcher.md"

    skill_text = skill_path.read_text(encoding="utf-8")
    pack_text = pack_path.read_text(encoding="utf-8")

    assert "references/packs/web-researcher.md" in skill_text
    assert len(skill_text.splitlines()) <= 105
    assert "## Fallback Chain" in pack_text
    assert "### Korean Law" in pack_text
    assert "### EU Law" in pack_text
    assert "## PDF/DOCX Source Handling" in pack_text
    assert "## Deterministic Search Executor" in pack_text


def test_api_acceptable_use_policy_uses_reference_pack() -> None:
    skill_path = ROOT / ".claude" / "skills" / "api-acceptable-use-policy" / "SKILL.md"
    pack_path = ROOT / "references" / "packs" / "api-acceptable-use-policy.md"

    skill_text = skill_path.read_text(encoding="utf-8")
    pack_text = pack_path.read_text(encoding="utf-8")

    assert "references/packs/api-acceptable-use-policy.md" in skill_text
    assert len(skill_text.splitlines()) <= 115
    assert "## AUP-to-License Allocation" in pack_text
    assert "## Prohibited Use Matrix" in pack_text
    assert "## Publication-Ready AUP Template" in pack_text
    assert "## Pitfalls" in pack_text


def test_ip_infringement_analysis_uses_reference_pack() -> None:
    skill_path = ROOT / ".claude" / "skills" / "ip-infringement-analysis" / "SKILL.md"
    pack_path = ROOT / "references" / "packs" / "ip-infringement-analysis.md"

    skill_text = skill_path.read_text(encoding="utf-8")
    pack_text = pack_path.read_text(encoding="utf-8")

    assert "references/packs/ip-infringement-analysis.md" in skill_text
    assert len(skill_text.splitlines()) <= 95
    assert "[VERIFY]" not in skill_text
    assert "[VERIFY]" not in pack_text
    assert "### Patent Infringement" in pack_text
    assert "### Trademark Infringement" in pack_text
    assert "### Copyright Infringement" in pack_text
    assert "### Trade Secret Misappropriation" in pack_text


def test_antitrust_investigation_summary_uses_reference_pack() -> None:
    skill_path = ROOT / ".claude" / "skills" / "antitrust-investigation-summary" / "SKILL.md"
    pack_path = ROOT / "references" / "packs" / "antitrust-investigation-summary.md"

    skill_text = skill_path.read_text(encoding="utf-8")
    pack_text = pack_path.read_text(encoding="utf-8")

    assert "references/packs/antitrust-investigation-summary.md" in skill_text
    assert len(skill_text.splitlines()) <= 85
    assert "[VERIFY]" not in skill_text
    assert "[VERIFY]" not in pack_text
    assert "## Section 4 — Key Findings" in pack_text
    assert "## Drafting Rules" in pack_text
    assert "### Anti-Hallucination" in pack_text
    assert "## Scope and Ethics" in pack_text


def test_cyber_law_compliance_summary_uses_reference_pack() -> None:
    skill_path = ROOT / ".claude" / "skills" / "cyber-law-compliance-summary" / "SKILL.md"
    pack_path = ROOT / "references" / "packs" / "cyber-law-compliance-summary.md"

    skill_text = skill_path.read_text(encoding="utf-8")
    pack_text = pack_path.read_text(encoding="utf-8")

    assert "references/packs/cyber-law-compliance-summary.md" in skill_text
    assert len(skill_text.splitlines()) <= 80
    assert "## Section 2 — Compliance Sections" in pack_text
    assert "## Section 3 — Jurisdiction Comparison Table" in pack_text
    assert "## Section 4 — Sensitive Data Categories" in pack_text
    assert "## Pitfalls and Checks" in pack_text


def test_output_generator_uses_reference_pack() -> None:
    skill_path = ROOT / ".claude" / "skills" / "output-generator" / "SKILL.md"
    pack_path = ROOT / "references" / "packs" / "output-generator.md"

    skill_text = skill_path.read_text(encoding="utf-8")
    pack_text = pack_path.read_text(encoding="utf-8")

    assert "references/packs/output-generator.md" in skill_text
    assert len(skill_text.splitlines()) <= 80
    assert "## Trust Boundary" in pack_text
    assert "## Mandatory Sections" in pack_text
    assert "## Citation Integrity Rules" in pack_text
    assert "## Format and Save Rules" in pack_text


def test_terms_of_service_uses_reference_pack() -> None:
    skill_path = ROOT / ".claude" / "skills" / "terms-of-service" / "SKILL.md"
    pack_path = ROOT / "references" / "packs" / "terms-of-service.md"

    skill_text = skill_path.read_text(encoding="utf-8")
    pack_text = pack_path.read_text(encoding="utf-8")

    assert "references/packs/terms-of-service.md" in skill_text
    assert len(skill_text.splitlines()) <= 80
    assert "## Intake Table" in pack_text
    assert "## Clause Selection" in pack_text
    assert "## Sample Clauses" in pack_text
    assert "## Final QC Checklist" in pack_text
