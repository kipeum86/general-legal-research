"""Validate Jinju Legal Orchestrator workflow checkpoint state.

The workflow is still agent-orchestrated, so this script focuses on the parts
that can be checked deterministically: step numbering, required artifacts, and
the conditional Step 9 citation-audit state.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


VALID_AUDIT_STATUSES = {"complete", "partial", "skipped", "failed"}
MEMO_DELIVERABLE_TOKENS = ("memo", "opinion", "legal_opinion", "formal_opinion", "의견서", "메모")


@dataclass
class WorkflowValidationResult:
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


def load_state(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_workflow_state(
    state: dict[str, Any],
    *,
    root: str | Path = ".",
    step: int | None = None,
    required_artifacts: list[str] | None = None,
) -> WorkflowValidationResult:
    root_path = Path(root)
    result = WorkflowValidationResult()

    _validate_step_fields(state, result)

    if step is not None and not 0 <= step <= 9:
        result.error(f"step must be between 0 and 9, got {step}")

    for spec in required_artifacts or []:
        _validate_required_artifact(spec, root_path, result)

    if step is not None and step >= 9:
        _validate_step9_state(state, root_path, result)

    return result


def should_run_step9(state: dict[str, Any]) -> bool:
    resolved = state.get("resolved_parameters")
    if not isinstance(resolved, dict):
        resolved = {}

    if _truthy(state.get("citation_audit_required")) or _truthy(resolved.get("citation_audit_required")):
        return True

    mode = str(state.get("last_mode") or state.get("output_mode") or resolved.get("mode") or "").strip().upper()
    if mode in {"B", "C", "D"}:
        return True

    if _truthy(state.get("legal_opinion_formatter_invoked")) or _truthy(resolved.get("legal_opinion_formatter_invoked")):
        return True

    deliverable_values = [
        state.get("deliverable_type"),
        state.get("requested_deliverable"),
        resolved.get("deliverable_type"),
        resolved.get("requested_deliverable"),
        resolved.get("output_type"),
    ]
    deliverable_text = " ".join(str(value).lower() for value in deliverable_values if value is not None)
    return any(token in deliverable_text for token in MEMO_DELIVERABLE_TOKENS)


def _validate_step_fields(state: dict[str, Any], result: WorkflowValidationResult) -> None:
    current = _normalize_step(state.get("current_step"), "current_step", result)
    last = _normalize_step(state.get("last_completed_step"), "last_completed_step", result)

    if current is not None and not 0 <= current <= 9:
        result.error(f"current_step must be between 0 and 9, got {current}")
    if last is not None and not 0 <= last <= 9:
        result.error(f"last_completed_step must be between 0 and 9, got {last}")
    if current is not None and last is not None and last > current:
        result.error(f"last_completed_step ({last}) cannot be greater than current_step ({current})")


def _validate_step9_state(state: dict[str, Any], root: Path, result: WorkflowValidationResult) -> None:
    step9_required = should_run_step9(state)
    audit_state = state.get("citation_audit")
    if not isinstance(audit_state, dict):
        audit_state = {}

    status = audit_state.get("status")
    if status is None:
        fired = state.get("citation_audit_fired")
        if fired is True:
            status = "complete"
        elif fired is False:
            status = "skipped"

    if not step9_required:
        if status in {"complete", "partial"}:
            result.warning("citation audit is marked complete even though Step 9 trigger conditions are not present")
        return

    if status is None:
        result.error("Step 9 is required but citation_audit.status or citation_audit_fired is missing")
        return
    if status not in VALID_AUDIT_STATUSES:
        result.error(f"citation_audit.status must be one of {sorted(VALID_AUDIT_STATUSES)}, got {status!r}")
        return

    reason = audit_state.get("reason") or state.get("citation_audit_skip_reason")
    if status in {"skipped", "failed"} and not reason:
        result.error(f"citation audit status {status!r} requires a reason")

    summary = audit_state.get("summary") or state.get("citation_audit_summary")
    if status in {"complete", "partial"} and not isinstance(summary, dict):
        result.error(f"citation audit status {status!r} requires a summary object")

    artifact = audit_state.get("artifact") or audit_state.get("json") or state.get("citation_audit_json")
    if artifact:
        artifact_path = _resolve_path(root, str(artifact))
        if not artifact_path.exists():
            result.error(f"citation audit artifact does not exist: {artifact_path}")


def _validate_required_artifact(spec: str, root: Path, result: WorkflowValidationResult) -> None:
    if "=" in spec:
        name, raw_path = spec.split("=", 1)
        name = name.strip() or "artifact"
    else:
        name = "artifact"
        raw_path = spec
    if not raw_path.strip():
        result.error(f"required artifact {name!r} has an empty path")
        return
    path = _resolve_path(root, raw_path.strip())
    if not path.exists():
        result.error(f"required artifact {name!r} does not exist: {path}")


def _normalize_step(value: Any, field_name: str, result: WorkflowValidationResult) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            return int(stripped)
    result.error(f"{field_name} must be an integer, numeric string, or null")
    return None


def _resolve_path(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return root / path


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate workflow checkpoint state.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate a checkpoint/workflow state JSON file.")
    validate.add_argument("--state", type=Path, default=Path("output/checkpoint.json"), help="State JSON file.")
    validate.add_argument("--root", type=Path, default=Path("."), help="Root directory for relative artifact paths.")
    validate.add_argument("--step", type=int, help="Step number being validated.")
    validate.add_argument(
        "--require-artifact",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Require an artifact path to exist. May be repeated.",
    )
    validate.add_argument("--quiet", action="store_true", help="Only use the exit status.")
    validate.set_defaults(func=_run_validate)
    return parser


def _run_validate(args: argparse.Namespace) -> int:
    try:
        state = load_state(args.state)
    except FileNotFoundError:
        print(json.dumps({"valid": False, "errors": [f"state file not found: {args.state}"], "warnings": []}, ensure_ascii=False, indent=2))
        return 1
    except json.JSONDecodeError as exc:
        print(json.dumps({"valid": False, "errors": [f"invalid JSON: {exc}"], "warnings": []}, ensure_ascii=False, indent=2))
        return 1

    result = validate_workflow_state(
        state,
        root=args.root,
        step=args.step,
        required_artifacts=args.require_artifact,
    )
    if not args.quiet:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    return 0 if result.valid else 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
