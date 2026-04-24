from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_runtime_prompts_do_not_use_legacy_verify_tag() -> None:
    checked_roots = [
        ROOT / ".claude" / "skills",
        ROOT / "references" / "packs",
    ]
    offenders: list[str] = []
    for checked_root in checked_roots:
        for path in checked_root.rglob("*.md"):
            if "[VERIFY]" in path.read_text(encoding="utf-8"):
                offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []
