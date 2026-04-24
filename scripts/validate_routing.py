"""Validate project skill routing table and representative routing fixtures."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_ROUTING_PATH = Path(__file__).resolve().parents[1] / ".claude" / "routing" / "skills.yaml"
DEFAULT_FIXTURES_PATH = Path(__file__).resolve().parents[1] / ".claude" / "routing" / "fixtures.yaml"
EXPECTED_CORE_STEPS = list(range(10))


@dataclass
class RoutingValidationResult:
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.valid = False
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "errors": self.errors, "warnings": self.warnings}


def load_jsonish(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def route_query(routing: dict[str, Any], query: str) -> list[str]:
    query_lower = query.lower()
    routed: list[str] = []
    for entry in routing.get("specialists", []):
        trigger_terms = entry.get("trigger_terms") or []
        if any(str(term).lower() in query_lower for term in trigger_terms):
            for skill in _entry_skills(entry):
                if skill not in routed:
                    routed.append(skill)
    return routed


def validate_routing_table(routing: dict[str, Any], *, root: str | Path = ".") -> RoutingValidationResult:
    root_path = Path(root)
    result = RoutingValidationResult()

    if routing.get("version") != 1:
        result.error("routing.version must be 1")

    core = routing.get("core_workflow")
    if not isinstance(core, list):
        result.error("core_workflow must be a list")
    else:
        steps = [entry.get("step") for entry in core if isinstance(entry, dict)]
        if steps != EXPECTED_CORE_STEPS:
            result.error(f"core_workflow steps must be {EXPECTED_CORE_STEPS}, got {steps}")
        for entry in core:
            if not isinstance(entry, dict):
                result.error("core_workflow entries must be objects")
                continue
            for skill in _entry_skills(entry):
                _validate_skill_exists(skill, root_path, result)
            canonical_spec = entry.get("canonical_spec")
            if canonical_spec and not (root_path / canonical_spec).exists():
                result.error(f"canonical_spec does not exist: {canonical_spec}")

    specialists = routing.get("specialists")
    if not isinstance(specialists, list) or not specialists:
        result.error("specialists must be a non-empty list")
    else:
        for index, entry in enumerate(specialists):
            if not isinstance(entry, dict):
                result.error(f"specialists[{index}] must be an object")
                continue
            skills = _entry_skills(entry)
            terms = entry.get("trigger_terms")
            if not skills:
                result.error(f"specialists[{index}] must declare skill(s)")
            if not isinstance(terms, list) or not terms:
                result.error(f"specialists[{index}].trigger_terms must be a non-empty list")
            for skill in skills:
                _validate_skill_exists(skill, root_path, result)
            for reference in entry.get("required_references", []) or []:
                if not (root_path / reference).exists():
                    result.error(f"required reference does not exist: {reference}")

    deep_researcher = routing.get("deep_researcher")
    if not isinstance(deep_researcher, dict):
        result.error("deep_researcher must be an object")
    else:
        agent = deep_researcher.get("agent")
        if not isinstance(agent, str) or not (root_path / agent).exists():
            result.error(f"deep_researcher.agent does not exist: {agent}")
        max_parallel = deep_researcher.get("max_parallel_researchers")
        if not isinstance(max_parallel, int) or max_parallel < 1:
            result.error("deep_researcher.max_parallel_researchers must be a positive integer")

    source_contract = routing.get("source_payload_contract")
    if not isinstance(source_contract, str) or not (root_path / source_contract).exists():
        result.error(f"source_payload_contract does not exist: {source_contract}")

    return result


def validate_fixtures(fixtures: dict[str, Any], routing: dict[str, Any]) -> RoutingValidationResult:
    result = RoutingValidationResult()
    if fixtures.get("schema_version") != "routing-fixtures/v1":
        result.error("fixtures.schema_version must be 'routing-fixtures/v1'")

    items = fixtures.get("fixtures")
    if not isinstance(items, list) or not items:
        result.error("fixtures.fixtures must be a non-empty list")
        return result

    seen_ids: set[str] = set()
    for index, fixture in enumerate(items):
        if not isinstance(fixture, dict):
            result.error(f"fixtures[{index}] must be an object")
            continue
        fixture_id = fixture.get("id")
        query = fixture.get("query")
        expected = fixture.get("expected_skills")
        if not isinstance(fixture_id, str) or not fixture_id:
            result.error(f"fixtures[{index}].id must be a non-empty string")
            continue
        if fixture_id in seen_ids:
            result.error(f"duplicate fixture id: {fixture_id}")
        seen_ids.add(fixture_id)
        if not isinstance(query, str) or not query.strip():
            result.error(f"fixture {fixture_id} query must be a non-empty string")
            continue
        if not isinstance(expected, list) or not all(isinstance(skill, str) for skill in expected):
            result.error(f"fixture {fixture_id} expected_skills must be a list of strings")
            continue
        actual = route_query(routing, query)
        missing = [skill for skill in expected if skill not in actual]
        if missing:
            result.error(f"fixture {fixture_id} missing expected skills {missing}; actual={actual}")
    return result


def _entry_skills(entry: dict[str, Any]) -> list[str]:
    if isinstance(entry.get("skill"), str):
        return [entry["skill"]]
    skills = entry.get("skills")
    if isinstance(skills, list):
        return [skill for skill in skills if isinstance(skill, str)]
    return []


def _validate_skill_exists(skill: str, root: Path, result: RoutingValidationResult) -> None:
    path = root / ".claude" / "skills" / skill / "SKILL.md"
    if not path.exists():
        result.error(f"skill does not exist: {skill} ({path})")


def merge_results(*results: RoutingValidationResult) -> RoutingValidationResult:
    merged = RoutingValidationResult()
    for result in results:
        for error in result.errors:
            merged.error(error)
        for warning in result.warnings:
            merged.warning(warning)
    return merged


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate skill routing table and representative fixtures.")
    parser.add_argument("--routing", type=Path, default=DEFAULT_ROUTING_PATH, help="Path to .claude/routing/skills.yaml.")
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES_PATH, help="Path to routing fixture file.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root.")
    parser.add_argument("--quiet", action="store_true", help="Only use the exit status.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        routing = load_jsonish(args.routing)
        fixtures = load_jsonish(args.fixtures)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        result = RoutingValidationResult(valid=False, errors=[str(exc)])
        if not args.quiet:
            print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
        return 1

    result = merge_results(
        validate_routing_table(routing, root=args.root),
        validate_fixtures(fixtures, routing),
    )
    if not args.quiet:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
