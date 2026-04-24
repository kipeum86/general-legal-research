"""Project-owned legal source priority registry helpers.

The registry file is named `legal_sources.yaml` for human-facing docs, but it is
kept as JSON-compatible YAML so this script can parse it with the standard
library and avoid adding a runtime dependency.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REGISTRY_SCHEMA_VERSION = "legal-source-registry/v1"
DEFAULT_REGISTRY_PATH = Path(__file__).resolve().parents[1] / "legal_sources.yaml"


@dataclass
class RegistryValidationResult:
    valid: bool = True
    errors: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.valid = False
        self.errors.append(message)

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "errors": self.errors}


def load_registry(path: str | Path = DEFAULT_REGISTRY_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_registry(registry: dict[str, Any]) -> RegistryValidationResult:
    result = RegistryValidationResult()
    if registry.get("schema_version") != REGISTRY_SCHEMA_VERSION:
        result.error(f"schema_version must be {REGISTRY_SCHEMA_VERSION!r}")

    jurisdictions = registry.get("jurisdictions")
    if not isinstance(jurisdictions, dict) or not jurisdictions:
        result.error("jurisdictions must be a non-empty object")
        return result

    if "DEFAULT" not in jurisdictions:
        result.error("jurisdictions.DEFAULT is required")

    for code, payload in jurisdictions.items():
        prefix = f"jurisdictions.{code}"
        if not isinstance(payload, dict):
            result.error(f"{prefix} must be an object")
            continue
        primary_sources = payload.get("primary_sources")
        fallback_order = payload.get("fallback_order")
        if not isinstance(primary_sources, list) or not primary_sources:
            result.error(f"{prefix}.primary_sources must be a non-empty list")
            continue
        source_ids = set()
        for index, source in enumerate(primary_sources):
            if not isinstance(source, dict):
                result.error(f"{prefix}.primary_sources[{index}] must be an object")
                continue
            source_id = source.get("id")
            if not isinstance(source_id, str) or not source_id:
                result.error(f"{prefix}.primary_sources[{index}].id must be a non-empty string")
                continue
            source_ids.add(source_id)
            if source.get("authority") != "primary":
                result.error(f"{prefix}.primary_sources[{index}].authority must be 'primary'")
            if source.get("grade") not in {"A", "B", "C", "D"}:
                result.error(f"{prefix}.primary_sources[{index}].grade must be A, B, C, or D")
        if not isinstance(fallback_order, list) or not fallback_order:
            result.error(f"{prefix}.fallback_order must be a non-empty list")
        elif not any(item in source_ids for item in fallback_order):
            result.error(f"{prefix}.fallback_order must reference at least one primary source id")
    return result


def get_jurisdiction(registry: dict[str, Any], jurisdiction: str) -> dict[str, Any]:
    jurisdictions = registry.get("jurisdictions") or {}
    code = jurisdiction.strip().upper()
    return jurisdictions.get(code) or jurisdictions["DEFAULT"]


def source_priority(
    registry: dict[str, Any],
    jurisdiction: str,
    *,
    korean_law_mcp_available: bool | None = None,
) -> dict[str, Any]:
    jurisdiction_payload = get_jurisdiction(registry, jurisdiction)
    primary_sources = list(jurisdiction_payload.get("primary_sources", []))
    fallback_order = list(jurisdiction_payload.get("fallback_order", []))
    degradation = []

    if jurisdiction.strip().upper() in {"KR", "KOR", "KOREA", "SOUTH KOREA", "REPUBLIC OF KOREA", "ROK"}:
        if korean_law_mcp_available is not True:
            disabled = [source["id"] for source in primary_sources if source.get("requires_mcp")]
            if disabled:
                primary_sources = [source for source in primary_sources if not source.get("requires_mcp")]
                fallback_order = [item for item in fallback_order if item not in disabled]
                degradation.append(
                    {
                        "scope": "KR",
                        "reason": "korean-law MCP unavailable or not declared available; falling back to persistent Open Law API and official portals.",
                        "disabled_sources": disabled,
                    }
                )

    return {
        "jurisdiction": jurisdiction.strip().upper(),
        "label": jurisdiction_payload.get("label"),
        "primary_sources": primary_sources,
        "secondary_sources": list(jurisdiction_payload.get("secondary_sources", [])),
        "fallback_order": fallback_order,
        "degradation": degradation,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and query legal_sources.yaml.")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH, help="Path to legal_sources.yaml.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate registry shape.")
    validate.set_defaults(func=_run_validate)

    show = subparsers.add_parser("show", help="Show source priority for a jurisdiction.")
    show.add_argument("jurisdiction")
    show.add_argument(
        "--korean-law-mcp-available",
        choices=["true", "false", "unknown"],
        default="unknown",
        help="Availability override for KR priority calculation.",
    )
    show.set_defaults(func=_run_show)
    return parser


def _run_validate(args: argparse.Namespace) -> int:
    try:
        registry = load_registry(args.registry)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1
    result = validate_registry(registry)
    print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    return 0 if result.valid else 1


def _run_show(args: argparse.Namespace) -> int:
    try:
        registry = load_registry(args.registry)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    availability = {"true": True, "false": False, "unknown": None}[args.korean_law_mcp_available]
    print(
        json.dumps(
            source_priority(registry, args.jurisdiction, korean_law_mcp_available=availability),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
