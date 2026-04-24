"""Project-owned backend helpers for citation-audit workflow hardening.

This module avoids editing the vendored `citation_auditor/` package. It adds
deterministic routing, claim-registry output, metrics, and Korean-law metadata
around the vendor aggregate JSON.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


VERIFIER_DEFINITIONS: dict[str, dict[str, Any]] = {
    "korean-law": {
        "authority": 1.0,
        "patterns": [
            r"제\s*\d+\s*조",
            r"민법|형법|상법|행정법|개인정보\s*보호법|개인정보보호법",
            r"\d+[다가나바도허]\d+",
        ],
    },
    "us-law": {
        "authority": 0.9,
        "patterns": [
            r"\b\d+\s*U\.?S\.?C\.?\s*§+\s*\d+[a-z0-9\-]*(?:\(\w+\))?",
            r"\b\d+\s*C\.?F\.?R\.?\s*§+\s*\d+\.\d+[a-z0-9\-]*",
            r"\b\d+\s*U\.?S\.?\s*\d+(?:\s*\(\d{4}\))?",
            r"\b[A-Z][A-Za-z\-'.]+\s+v\.\s+[A-Z][A-Za-z\-'.]+\b",
        ],
    },
    "eu-law": {
        "authority": 0.9,
        "patterns": [
            r"\bCELEX:?\s*\d+[A-Z]\d+\b",
            r"\bRegulation \(EU\)\s*(?:No\s*)?\d+/\d+\b",
            r"\bDirective\s*\d+/\d+(?:/EU|/EC)?\b",
            r"\b(?:GDPR|DSA|DMA|AI Act|eIDAS|MiCA|NIS\s*2|Copyright Directive|Data Act)\b",
        ],
    },
    "uk-law": {
        "authority": 0.9,
        "patterns": [
            r"\[(?:19|20)\d{2}\]\s*(?:UKSC|UKHL|UKPC|EWCA\s*(?:Civ|Crim)|EWHC|UKUT|UKFTT|UKEAT|CSIH|CSOH|HCA)\s*\d+",
            r"\b[A-Z][\w\-']+\s+v\s+[A-Z][\w\-']+",
            r"\b[A-Z][\w\s]{1,60}?\s+Act\s+(?:19|20)\d{2}\b",
            r"\bR\s+\(?on the application of\s+[A-Z]|\bR\s+v\s+[A-Z]",
        ],
    },
    "scholarly": {
        "authority": 0.9,
        "patterns": [
            r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+",
            r"\barXiv:\s*\d{4}\.\d{4,5}",
            r"\bPMID:?\s*\d{5,9}",
            r"\b(Nature|Science|Lancet|NEJM|Cell|JAMA|BMJ|PNAS|PLoS|IEEE|ACM)\b",
        ],
    },
    "wikipedia": {
        "authority": 0.7,
        "patterns": [
            r"\b(?:founded|established|born|died|signed|published|released|invented) in \d{3,4}",
            r"\b(?:in|on) \d{3,4}\b.{0,60}?(?:Treaty|Convention|Declaration|Amendment|Dynasty|Empire|Revolution|War)",
            r"\bThe (?:first|last) .{1,60}? was",
            r"\b(?:CEO|founder|president|king|queen|emperor) of [A-Z]",
        ],
    },
    "general-web": {
        "authority": 0.5,
        "patterns": [r".*"],
    },
}

JURISDICTION_ROUTES = {
    "KR": "korean-law",
    "KOR": "korean-law",
    "KOREA": "korean-law",
    "SOUTH KOREA": "korean-law",
    "REPUBLIC OF KOREA": "korean-law",
    "ROK": "korean-law",
    "대한민국": "korean-law",
    "한국": "korean-law",
    "US": "us-law",
    "USA": "us-law",
    "UNITED STATES": "us-law",
    "EU": "eu-law",
    "EUROPEAN UNION": "eu-law",
    "UK": "uk-law",
    "UNITED KINGDOM": "uk-law",
}

DETAILED_STATUSES = {
    "verified",
    "contradicted",
    "unsupported",
    "source_unavailable",
    "verifier_unavailable",
    "not_a_legal_claim",
    "unknown",
}

SCHEMA_VERSION = "citation-audit-backend/v1"
CLAIM_REGISTRY_SCHEMA_VERSION = "claim-registry/v1"
CITATION_AUDIT_METADATA_SCHEMA_VERSION = "citation-audit-metadata/v1"
PLACEHOLDER_ENV_VALUES = {"", "your_openlaw_oc", "todo", "changeme", "replace_me", "placeholder"}


@dataclass(frozen=True)
class RouteDecision:
    verifier: str
    authority: float
    reason: str
    matched_pattern: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "verifier": self.verifier,
            "authority": self.authority,
            "reason": self.reason,
            "matched_pattern": self.matched_pattern,
        }


def route_claim(claim: dict[str, Any]) -> list[RouteDecision]:
    text = str(claim.get("text") or "")
    decisions: list[RouteDecision] = []

    suggested = claim.get("suggested_verifier")
    if isinstance(suggested, str) and suggested in VERIFIER_DEFINITIONS:
        return [_decision(suggested, "suggested_verifier")]

    jurisdiction = claim.get("jurisdiction") or claim.get("jurisdiction_hint")
    if isinstance(jurisdiction, str):
        verifier = JURISDICTION_ROUTES.get(jurisdiction.strip().upper())
        if verifier:
            decisions.append(_decision(verifier, "explicit_jurisdiction"))

    authority_type = str(claim.get("authority_type") or "").lower()
    if authority_type in {"paper", "academic", "scholarly", "doi", "journal"}:
        decisions.append(_decision("scholarly", "authority_type"))
    if authority_type in {"statute", "case", "legal_primary", "law"} and not decisions:
        domain = str(claim.get("legal_domain") or claim.get("jurisdiction") or "").upper()
        verifier = JURISDICTION_ROUTES.get(domain)
        if verifier:
            decisions.append(_decision(verifier, "authority_type_and_domain"))

    for verifier, definition in VERIFIER_DEFINITIONS.items():
        if verifier == "general-web":
            continue
        for pattern in definition["patterns"]:
            if re.search(pattern, text, flags=re.IGNORECASE):
                decisions.append(_decision(verifier, "pattern", pattern))
                break

    if not decisions:
        decisions.append(_decision("general-web", "fallback"))

    return _dedupe_routes(decisions)


def normalize_verdict_status(verdict: dict[str, Any]) -> str:
    label = str(verdict.get("label") or "").strip().lower()
    verifier_name = str(verdict.get("verifier_name") or "").strip().lower()
    rationale = str(verdict.get("rationale") or "").strip()
    evidence = verdict.get("evidence") or []

    if label == "verified":
        return "verified"
    if label == "contradicted":
        return "contradicted"
    if label == "not_a_legal_claim":
        return "not_a_legal_claim"
    if verifier_name in {"", "none"}:
        return "verifier_unavailable"
    if "원문 조회 실패" in rationale or "source unavailable" in rationale.lower():
        return "source_unavailable"
    if label == "unknown" and not evidence:
        return "unsupported"
    return "unknown" if label else "verifier_unavailable"


def build_claim_registry(aggregate: dict[str, Any]) -> dict[str, Any]:
    claims = []
    for item in aggregate.get("aggregated", []):
        claim = item.get("claim") or {}
        verdict = item.get("verdict") or {}
        routes = [route.as_dict() for route in route_claim(claim)]
        claims.append(
            {
                "claim_id": claim_id(claim),
                "text": claim.get("text", ""),
                "sentence_span": claim.get("sentence_span", {}),
                "claim_type": claim.get("claim_type"),
                "routing": routes,
                "verdict": verdict,
                "normalized_status": normalize_verdict_status(verdict),
            }
        )
    return {"schema_version": CLAIM_REGISTRY_SCHEMA_VERSION, "claims": claims}


def compute_metrics(aggregate: dict[str, Any]) -> dict[str, Any]:
    items = list(aggregate.get("aggregated", []))
    statuses = [normalize_verdict_status(item.get("verdict") or {}) for item in items]
    total = len(items)
    audited = sum(1 for status in statuses if status != "not_a_legal_claim")
    metrics = {
        "total_claims": total,
        "audited_claims": audited,
        "verified": statuses.count("verified"),
        "contradicted": statuses.count("contradicted"),
        "unsupported": statuses.count("unsupported"),
        "source_unavailable": statuses.count("source_unavailable"),
        "verifier_unavailable": statuses.count("verifier_unavailable"),
        "unknown": statuses.count("unknown"),
        "tool_failures": statuses.count("source_unavailable") + statuses.count("verifier_unavailable"),
        "coverage_ratio": round((audited - statuses.count("verifier_unavailable")) / audited, 4) if audited else 1.0,
    }
    return metrics


def build_metadata(
    aggregate: dict[str, Any],
    *,
    korean_law_mcp_available: bool | None = None,
) -> dict[str, Any]:
    registry = build_claim_registry(aggregate)
    metrics = compute_metrics(aggregate)
    korean_claims = [
        claim
        for claim in registry["claims"]
        if any(route["verifier"] == "korean-law" for route in claim["routing"])
    ]
    degradation = []
    if korean_claims and korean_law_mcp_available is not True:
        degradation.append(
            {
                "scope": "korean-law",
                "reason": "korean-law MCP unavailable or not declared available; primary-law verification may degrade to unknown.",
                "affected_claim_ids": [claim["claim_id"] for claim in korean_claims],
            }
        )
    audit_status = "partial" if metrics["tool_failures"] or degradation else "complete"
    return {
        "schema_version": CITATION_AUDIT_METADATA_SCHEMA_VERSION,
        "backend_schema_version": SCHEMA_VERSION,
        "audit_status": audit_status,
        "metrics": metrics,
        "korean_law_mcp_available": korean_law_mcp_available,
        "source_degradation": degradation,
    }


def validate_aggregate_shape(aggregate: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(aggregate, dict):
        return ["aggregate must be an object"]
    items = aggregate.get("aggregated")
    if not isinstance(items, list):
        return ["aggregate must contain an 'aggregated' list"]

    for index, item in enumerate(items):
        prefix = f"aggregated[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue

        claim = item.get("claim")
        verdict = item.get("verdict")
        if not isinstance(claim, dict):
            errors.append(f"{prefix}.claim must be an object")
        else:
            text = claim.get("text")
            span = claim.get("sentence_span")
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{prefix}.claim.text must be a non-empty string")
            if not isinstance(span, dict):
                errors.append(f"{prefix}.claim.sentence_span must be an object")
            else:
                start = span.get("start")
                end = span.get("end")
                if not isinstance(start, int) or not isinstance(end, int):
                    errors.append(f"{prefix}.claim.sentence_span.start/end must be integers")
                elif start < 0 or end < start:
                    errors.append(f"{prefix}.claim.sentence_span must satisfy 0 <= start <= end")

        if not isinstance(verdict, dict):
            errors.append(f"{prefix}.verdict must be an object")
        else:
            label = verdict.get("label")
            evidence = verdict.get("evidence", [])
            if label is not None and not isinstance(label, str):
                errors.append(f"{prefix}.verdict.label must be a string when present")
            if not isinstance(evidence, list):
                errors.append(f"{prefix}.verdict.evidence must be a list")
    return errors


def claim_id(claim: dict[str, Any]) -> str:
    text = " ".join(str(claim.get("text") or "").split())
    span = claim.get("sentence_span") or {}
    material = f"{text}|{span.get('start')}|{span.get('end')}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def load_alias_table(path: str | Path | None = None) -> dict[str, Any]:
    if path is None:
        path = Path(__file__).resolve().parents[1] / "data" / "korean_law_aliases.json"
    return json.loads(Path(path).read_text(encoding="utf-8"))


def lookup_korean_law_alias(name: str, table: dict[str, Any] | None = None) -> dict[str, Any]:
    aliases = table or load_alias_table()
    normalized = _normalize_law_name(name)
    for alias, payload in aliases.items():
        if _normalize_law_name(alias) == normalized:
            return {"name": alias, **payload}
    return {"name": name, "law_id": None, "verified": False, "source": "not found in local alias table"}


def detect_korean_law_mcp_availability(root: str | Path | None = None) -> bool | None:
    """Best-effort local availability signal without network/tool execution.

    `True` means a Korean-law MCP server is configured and has a non-placeholder
    LAW_OC value available in the process environment or `.mcp.json`.
    `False` means the server is referenced but only with a placeholder/missing
    credential. `None` means no local signal was found.
    """
    env_value = os.environ.get("KOREAN_LAW_MCP_AVAILABLE")
    if env_value is not None and env_value.strip().lower() not in {"auto", "unknown", "none"}:
        try:
            return _parse_boolish(env_value, root=root)
        except ValueError:
            return None

    law_oc = os.environ.get("LAW_OC")
    if law_oc and law_oc.strip().lower() not in PLACEHOLDER_ENV_VALUES:
        return True

    root_path = Path(root) if root is not None else Path.cwd()
    config_path = root_path / ".mcp.json"
    if not config_path.exists():
        return None

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None

    servers = config.get("mcpServers")
    if not isinstance(servers, dict):
        return None

    for name, server in servers.items():
        server_blob = json.dumps(server, ensure_ascii=False).lower()
        if "korean-law" not in str(name).lower() and "korean-law-mcp" not in server_blob:
            continue
        if not isinstance(server, dict):
            return False
        configured_env = server.get("env") if isinstance(server.get("env"), dict) else {}
        configured_law_oc = os.environ.get("LAW_OC") or configured_env.get("LAW_OC")
        if configured_law_oc and str(configured_law_oc).strip().lower() not in PLACEHOLDER_ENV_VALUES:
            return True
        return False
    return None


def _decision(verifier: str, reason: str, pattern: str | None = None) -> RouteDecision:
    definition = VERIFIER_DEFINITIONS[verifier]
    return RouteDecision(verifier=verifier, authority=float(definition["authority"]), reason=reason, matched_pattern=pattern)


def _dedupe_routes(routes: list[RouteDecision]) -> list[RouteDecision]:
    deduped: dict[str, RouteDecision] = {}
    for route in routes:
        existing = deduped.get(route.verifier)
        if existing is None or existing.reason == "fallback":
            deduped[route.verifier] = route
    return sorted(deduped.values(), key=lambda route: route.authority, reverse=True)


def _normalize_law_name(value: str) -> str:
    return re.sub(r"\s+", "", value.strip())


def _read_json_input(value: str | Path) -> dict[str, Any]:
    if str(value) == "-":
        return json.loads(sys.stdin.read())
    return json.loads(Path(value).read_text(encoding="utf-8"))


def _parse_boolish(value: str, *, root: str | Path | None = None) -> bool | None:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "y", "available"}:
        return True
    if lowered in {"0", "false", "no", "n", "unavailable"}:
        return False
    if lowered in {"auto", "unknown", "none"}:
        env = os.environ.get("KOREAN_LAW_MCP_AVAILABLE")
        if env is None or env.strip().lower() in {"auto", "unknown", "none"}:
            return detect_korean_law_mcp_availability(root=root)
        return _parse_boolish(env, root=root)
    raise ValueError(f"Unsupported boolean value: {value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project-owned citation audit backend helpers.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    route_parser = subparsers.add_parser("route", help="Route a claim JSON object to verifier ids.")
    route_parser.add_argument("claim_json", help="Claim JSON string, JSON file path, or - for stdin.")
    route_parser.set_defaults(func=_run_route)

    enrich_parser = subparsers.add_parser("enrich", help="Validate/enrich aggregate JSON into registry and metadata.")
    enrich_parser.add_argument("aggregated_json", help="AggregateOutput JSON path or - for stdin.")
    enrich_parser.add_argument("--registry-out", type=Path, help="Write claim registry JSON.")
    enrich_parser.add_argument("--metadata-out", type=Path, help="Write audit metadata JSON.")
    enrich_parser.add_argument("--project-root", type=Path, default=Path("."), help="Project root for local MCP config detection.")
    enrich_parser.add_argument(
        "--korean-law-mcp-available",
        default="auto",
        help="true/false/auto. Auto reads KOREAN_LAW_MCP_AVAILABLE if set.",
    )
    enrich_parser.set_defaults(func=_run_enrich)

    lookup_parser = subparsers.add_parser("lookup-korean-law", help="Look up local Korean law alias metadata.")
    lookup_parser.add_argument("name")
    lookup_parser.set_defaults(func=_run_lookup_korean_law)

    return parser


def _run_route(args: argparse.Namespace) -> int:
    try:
        if args.claim_json == "-":
            claim = json.loads(sys.stdin.read())
        else:
            path = Path(args.claim_json)
            claim = json.loads(path.read_text(encoding="utf-8")) if path.exists() else json.loads(args.claim_json)
        print(json.dumps({"routes": [route.as_dict() for route in route_claim(claim)]}, ensure_ascii=False, indent=2))
        return 0
    except json.JSONDecodeError as exc:
        print(f"invalid claim JSON: {exc}", file=sys.stderr)
        return 1


def _run_enrich(args: argparse.Namespace) -> int:
    try:
        aggregate = _read_json_input(args.aggregated_json)
        korean_law_mcp_available = _parse_boolish(args.korean_law_mcp_available, root=args.project_root)
    except (json.JSONDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    errors = validate_aggregate_shape(aggregate)
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    registry = build_claim_registry(aggregate)
    metadata = build_metadata(aggregate, korean_law_mcp_available=korean_law_mcp_available)
    payload = {"registry": registry, "metadata": metadata}

    if args.registry_out:
        args.registry_out.parent.mkdir(parents=True, exist_ok=True)
        args.registry_out.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.metadata_out:
        args.metadata_out.parent.mkdir(parents=True, exist_ok=True)
        args.metadata_out.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _run_lookup_korean_law(args: argparse.Namespace) -> int:
    print(json.dumps(lookup_korean_law_alias(args.name), ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
