import importlib.util
import subprocess
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "legal_source_registry.py"
SPEC = importlib.util.spec_from_file_location("legal_source_registry", MODULE_PATH)
legal_source_registry = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = legal_source_registry
SPEC.loader.exec_module(legal_source_registry)


def test_registry_validates_default_file() -> None:
    registry = legal_source_registry.load_registry()
    result = legal_source_registry.validate_registry(registry)

    assert result.valid
    assert result.errors == []


def test_korean_law_mcp_is_first_when_available() -> None:
    registry = legal_source_registry.load_registry()

    priority = legal_source_registry.source_priority(registry, "KR", korean_law_mcp_available=True)

    assert priority["primary_sources"][0]["id"] == "korean-law-mcp"
    assert priority["fallback_order"][0] == "korean-law-mcp"
    assert priority["degradation"] == []


def test_korean_law_mcp_unavailable_falls_back_to_open_law_api() -> None:
    registry = legal_source_registry.load_registry()

    priority = legal_source_registry.source_priority(registry, "KR", korean_law_mcp_available=False)

    assert priority["primary_sources"][0]["id"] == "open_law_api"
    assert "korean-law-mcp" not in priority["fallback_order"]
    assert priority["degradation"][0]["disabled_sources"] == ["korean-law-mcp"]


def test_unknown_jurisdiction_uses_default_registry() -> None:
    registry = legal_source_registry.load_registry()

    priority = legal_source_registry.source_priority(registry, "BR")

    assert priority["label"] == "Default jurisdiction"
    assert priority["primary_sources"][0]["id"] == "official_portal"


def test_cli_validate_registry() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/legal_source_registry.py", "validate"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert '"valid": true' in result.stdout
