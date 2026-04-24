import importlib.util
import json
import subprocess
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "citation_audit_backend.py"
SPEC = importlib.util.spec_from_file_location("citation_audit_backend", MODULE_PATH)
citation_audit_backend = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = citation_audit_backend
SPEC.loader.exec_module(citation_audit_backend)


def _aggregate_item(
    text: str,
    *,
    label: str = "verified",
    verifier_name: str = "test-verifier",
    rationale: str = "ok",
    evidence: list[dict] | None = None,
    **claim_fields,
) -> dict:
    end = claim_fields.pop("end", len(text))
    claim = {
        "text": text,
        "sentence_span": {"start": claim_fields.pop("start", 0), "end": end},
        "claim_type": claim_fields.pop("claim_type", "citation"),
        **claim_fields,
    }
    return {
        "claim": claim,
        "verdict": {
            "label": label,
            "verifier_name": verifier_name,
            "authority": 0.9,
            "rationale": rationale,
            "evidence": evidence if evidence is not None else [{"url": "https://example.test/source"}],
        },
    }


def test_suggested_verifier_wins_over_pattern_route() -> None:
    routes = citation_audit_backend.route_claim(
        {
            "text": "민법 제750조 and DOI 10.1000/example are mentioned.",
            "sentence_span": {"start": 0, "end": 10},
            "suggested_verifier": "scholarly",
        }
    )

    assert [route.verifier for route in routes] == ["scholarly"]
    assert routes[0].reason == "suggested_verifier"


def test_korean_law_claim_routes_and_records_mcp_degradation() -> None:
    aggregate = {
        "aggregated": [
            _aggregate_item(
                "민법 제750조는 불법행위 책임을 정한다.",
                label="unknown",
                verifier_name="none",
                evidence=[],
                jurisdiction="KR",
            )
        ]
    }

    registry = citation_audit_backend.build_claim_registry(aggregate)
    metadata = citation_audit_backend.build_metadata(aggregate, korean_law_mcp_available=False)

    claim = registry["claims"][0]
    assert registry["schema_version"] == "claim-registry/v1"
    assert claim["routing"][0]["verifier"] == "korean-law"
    assert claim["routing"][0]["reason"] == "explicit_jurisdiction"
    assert claim["normalized_status"] == "verifier_unavailable"
    assert metadata["audit_status"] == "partial"
    assert metadata["source_degradation"][0]["scope"] == "korean-law"
    assert claim["claim_id"] in metadata["source_degradation"][0]["affected_claim_ids"]


def test_general_claim_falls_back_to_general_web() -> None:
    routes = citation_audit_backend.route_claim({"text": "The company launched a product in 2024."})

    assert routes[0].verifier == "general-web"
    assert routes[0].reason == "fallback"


def test_metrics_use_detailed_verdict_statuses() -> None:
    aggregate = {
        "aggregated": [
            _aggregate_item("Verified claim.", label="verified"),
            _aggregate_item("Contradicted claim.", label="contradicted"),
            _aggregate_item("Unsupported claim.", label="unknown", verifier_name="web", evidence=[]),
            _aggregate_item("Unavailable source.", label="unknown", verifier_name="korean-law", rationale="원문 조회 실패", evidence=[]),
            _aggregate_item("No verifier.", label="unknown", verifier_name="none", evidence=[]),
            _aggregate_item("Not legal.", label="not_a_legal_claim", verifier_name="none", evidence=[]),
        ]
    }

    metrics = citation_audit_backend.compute_metrics(aggregate)

    assert metrics["total_claims"] == 6
    assert metrics["audited_claims"] == 5
    assert metrics["verified"] == 1
    assert metrics["contradicted"] == 1
    assert metrics["unsupported"] == 1
    assert metrics["source_unavailable"] == 1
    assert metrics["verifier_unavailable"] == 1
    assert metrics["tool_failures"] == 2
    assert metrics["coverage_ratio"] == 0.8


def test_claim_id_is_stable_for_equivalent_whitespace() -> None:
    first = citation_audit_backend.claim_id({"text": "민법  제750조", "sentence_span": {"start": 1, "end": 9}})
    second = citation_audit_backend.claim_id({"text": "민법 제750조", "sentence_span": {"start": 1, "end": 9}})

    assert first == second


def test_korean_law_alias_lookup_distinguishes_verified_and_unverified_aliases() -> None:
    verified = citation_audit_backend.lookup_korean_law_alias("개인정보보호법")
    unverified = citation_audit_backend.lookup_korean_law_alias("형법")
    missing = citation_audit_backend.lookup_korean_law_alias("없는법")

    assert verified["law_id"] == "011357"
    assert verified["verified"] is True
    assert unverified["law_id"] is None
    assert unverified["verified"] is False
    assert missing["source"] == "not found in local alias table"


def test_detect_korean_law_mcp_availability_from_local_config(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("KOREAN_LAW_MCP_AVAILABLE", raising=False)
    monkeypatch.delenv("LAW_OC", raising=False)
    (tmp_path / ".mcp.json").write_text(
        json.dumps(
            {
                "mcpServers": {
                    "korean-law": {
                        "command": "npx",
                        "args": ["-y", "korean-law-mcp@latest"],
                        "env": {"LAW_OC": "your_openlaw_oc"},
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    assert citation_audit_backend.detect_korean_law_mcp_availability(tmp_path) is False

    monkeypatch.setenv("LAW_OC", "real-key")
    assert citation_audit_backend.detect_korean_law_mcp_availability(tmp_path) is True


def test_cli_enrich_writes_registry_and_metadata(tmp_path: Path) -> None:
    aggregate_path = tmp_path / "aggregate.json"
    registry_path = tmp_path / "claim-registry.json"
    metadata_path = tmp_path / "metadata.json"
    aggregate_path.write_text(
        json.dumps({"aggregated": [_aggregate_item("민법 제750조", jurisdiction="KR")]}),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/citation_audit_backend.py",
            "enrich",
            str(aggregate_path),
            "--registry-out",
            str(registry_path),
            "--metadata-out",
            str(metadata_path),
            "--korean-law-mcp-available",
            "false",
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert registry["claims"][0]["routing"][0]["verifier"] == "korean-law"
    assert metadata["source_degradation"][0]["scope"] == "korean-law"


def test_cli_enrich_rejects_malformed_aggregate(tmp_path: Path) -> None:
    aggregate_path = tmp_path / "bad.json"
    aggregate_path.write_text(json.dumps({"aggregated": [{"claim": {"text": ""}, "verdict": {}}]}), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/citation_audit_backend.py", "enrich", str(aggregate_path)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "claim.text" in result.stderr


def test_cli_enrich_rejects_non_object_aggregate(tmp_path: Path) -> None:
    aggregate_path = tmp_path / "bad.json"
    aggregate_path.write_text(json.dumps([]), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/citation_audit_backend.py", "enrich", str(aggregate_path)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "aggregate must be an object" in result.stderr
