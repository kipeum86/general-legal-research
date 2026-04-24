import importlib.util
import json
import subprocess
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "workflow_state.py"
SPEC = importlib.util.spec_from_file_location("workflow_state", MODULE_PATH)
workflow_state = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = workflow_state
SPEC.loader.exec_module(workflow_state)


def test_step9_required_without_audit_state_fails() -> None:
    state = {
        "current_step": 9,
        "last_completed_step": 8,
        "last_mode": "D",
        "resolved_parameters": {},
    }

    result = workflow_state.validate_workflow_state(state, step=9)

    assert not result.valid
    assert any("Step 9 is required" in error for error in result.errors)


def test_step9_complete_with_existing_artifact_passes(tmp_path: Path) -> None:
    artifact = tmp_path / "citation-audit-session.json"
    artifact.write_text("{}", encoding="utf-8")
    state = {
        "current_step": 9,
        "last_completed_step": 9,
        "last_mode": "D",
        "citation_audit": {
            "status": "complete",
            "artifact": str(artifact),
            "summary": {"verified": 1, "contradicted": 0, "unknown": 0},
        },
    }

    result = workflow_state.validate_workflow_state(state, step=9, root=tmp_path)

    assert result.valid
    assert result.errors == []


def test_invalid_step_transition_fails() -> None:
    state = {
        "current_step": 3,
        "last_completed_step": 8,
        "resolved_parameters": {},
    }

    result = workflow_state.validate_workflow_state(state)

    assert not result.valid
    assert any("cannot be greater" in error for error in result.errors)


def test_missing_required_artifact_fails(tmp_path: Path) -> None:
    state = {
        "current_step": 7,
        "last_completed_step": 6,
        "resolved_parameters": {},
    }

    result = workflow_state.validate_workflow_state(
        state,
        root=tmp_path,
        required_artifacts=["final_docx=output/missing.docx"],
    )

    assert not result.valid
    assert any("final_docx" in error for error in result.errors)


def test_cli_validate_returns_nonzero_for_missing_step9_state(tmp_path: Path) -> None:
    state_path = tmp_path / "checkpoint.json"
    state_path.write_text(
        json.dumps({"current_step": 9, "last_completed_step": 8, "last_mode": "B"}),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "scripts/workflow_state.py", "validate", "--state", str(state_path), "--step", "9"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Step 9 is required" in result.stdout
