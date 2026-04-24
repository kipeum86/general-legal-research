import importlib.util
import subprocess
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_routing.py"
SPEC = importlib.util.spec_from_file_location("validate_routing", MODULE_PATH)
validate_routing = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = validate_routing
SPEC.loader.exec_module(validate_routing)


def test_default_routing_table_validates() -> None:
    root = Path(__file__).resolve().parents[1]
    routing = validate_routing.load_jsonish(root / ".claude" / "routing" / "skills.yaml")

    result = validate_routing.validate_routing_table(routing, root=root)

    assert result.valid
    assert result.errors == []


def test_default_routing_fixtures_validate() -> None:
    root = Path(__file__).resolve().parents[1]
    routing = validate_routing.load_jsonish(root / ".claude" / "routing" / "skills.yaml")
    fixtures = validate_routing.load_jsonish(root / ".claude" / "routing" / "fixtures.yaml")

    result = validate_routing.validate_fixtures(fixtures, routing)

    assert result.valid
    assert result.errors == []


def test_route_query_matches_multiple_expected_skills() -> None:
    root = Path(__file__).resolve().parents[1]
    routing = validate_routing.load_jsonish(root / ".claude" / "routing" / "skills.yaml")

    routed = validate_routing.route_query(
        routing,
        "Review our API acceptable use policy and terms of service for platform users.",
    )

    assert routed == ["terms-of-service", "api-acceptable-use-policy"]


def test_validate_routing_table_rejects_missing_skill(tmp_path: Path) -> None:
    routing = {
        "version": 1,
        "core_workflow": [{"step": index, "skill": "missing-skill"} for index in range(10)],
        "specialists": [{"skills": ["missing-skill"], "trigger_terms": ["missing"]}],
        "deep_researcher": {"agent": ".claude/agents/deep-researcher/AGENT.md", "max_parallel_researchers": 1},
        "source_payload_contract": "references/source-payload-contract.md",
    }

    result = validate_routing.validate_routing_table(routing, root=tmp_path)

    assert not result.valid
    assert any("skill does not exist: missing-skill" in error for error in result.errors)


def test_cli_validate_routing() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_routing.py"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert '"valid": true' in result.stdout
