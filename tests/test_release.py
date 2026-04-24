import importlib.util
import subprocess
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "release.py"
SPEC = importlib.util.spec_from_file_location("release", MODULE_PATH)
release = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = release
SPEC.loader.exec_module(release)


def _write_release_tree(root: Path, version: str = "v1.2.3") -> None:
    (root / "docs" / "releases").mkdir(parents=True)
    (root / "docs" / "releases" / f"{version}.md").write_text(f"# {version} - Test Release\n\nBody.\n", encoding="utf-8")
    (root / "README.md").write_text(
        f"> Latest release: **[{version} - Test Release](docs/releases/{version}.md)**\n",
        encoding="utf-8",
    )


def _git_stub(tag_commit: str = "abc", head_commit: str = "abc"):
    def _git(_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        if args[:3] == ("rev-list", "-n", "1"):
            return subprocess.CompletedProcess(["git", *args], 0, stdout=f"{tag_commit}\n", stderr="")
        if args == ("rev-parse", "HEAD"):
            return subprocess.CompletedProcess(["git", *args], 0, stdout=f"{head_commit}\n", stderr="")
        return subprocess.CompletedProcess(["git", *args], 1, stdout="", stderr="unexpected git call")

    return _git


def test_validate_release_accepts_matching_note_readme_and_tag(tmp_path: Path, monkeypatch) -> None:
    _write_release_tree(tmp_path)
    monkeypatch.setattr(release, "_git", _git_stub())

    result = release.validate_release("v1.2.3", root=tmp_path, require_tag_at_head=True)

    assert result.valid
    assert result.errors == []


def test_validate_release_fails_when_readme_points_elsewhere(tmp_path: Path, monkeypatch) -> None:
    _write_release_tree(tmp_path, version="v1.2.3")
    monkeypatch.setattr(release, "_git", _git_stub())

    result = release.validate_release("v1.2.4", root=tmp_path)

    assert not result.valid
    assert any("release note missing" in error for error in result.errors)
    assert any("README.md latest release points to v1.2.3" in error for error in result.errors)


def test_validate_release_fails_when_tag_is_not_head(tmp_path: Path, monkeypatch) -> None:
    _write_release_tree(tmp_path)
    monkeypatch.setattr(release, "_git", _git_stub(tag_commit="abc", head_commit="def"))

    result = release.validate_release("v1.2.3", root=tmp_path, require_tag_at_head=True)

    assert not result.valid
    assert "tag v1.2.3 does not point at HEAD" in result.errors


def test_cli_validate_current_release_without_head_requirement() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/release.py", "validate", "v1.1.0"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert '"valid": true' in result.stdout
