"""Release preflight checks for local release notes, tags, and docs links."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


VERSION_RE = re.compile(r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")
README_RELEASE_RE = re.compile(r"Latest release:\s+\*\*\[[^\]]+\]\(docs/releases/(?P<version>v\d+\.\d+\.\d+)\.md\)\*\*")


@dataclass
class ReleaseValidationResult:
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


def validate_release(
    version: str,
    *,
    root: str | Path = ".",
    require_tag_at_head: bool = False,
    github_body_file: str | Path | None = None,
) -> ReleaseValidationResult:
    root_path = Path(root)
    result = ReleaseValidationResult()

    if not VERSION_RE.match(version):
        result.error(f"version must look like vX.Y.Z, got {version!r}")
        return result

    release_note = root_path / "docs" / "releases" / f"{version}.md"
    if not release_note.exists():
        result.error(f"release note missing: {release_note}")
    else:
        text = release_note.read_text(encoding="utf-8")
        if not text.lstrip().startswith(f"# {version}"):
            result.error(f"release note must start with '# {version}'")

    readme_path = root_path / "README.md"
    if not readme_path.exists():
        result.error("README.md missing")
    else:
        readme_text = readme_path.read_text(encoding="utf-8")
        match = README_RELEASE_RE.search(readme_text)
        if not match:
            result.error("README.md latest release link is missing or not in the expected format")
        elif match.group("version") != version:
            result.error(f"README.md latest release points to {match.group('version')}, expected {version}")

    tag_commit = _git(root_path, "rev-list", "-n", "1", version)
    if tag_commit.returncode != 0:
        result.error(f"git tag missing: {version}")
    elif require_tag_at_head:
        head_commit = _git(root_path, "rev-parse", "HEAD")
        if head_commit.returncode != 0:
            result.error(f"could not resolve HEAD: {head_commit.stderr.strip()}")
        elif tag_commit.stdout.strip() != head_commit.stdout.strip():
            result.error(f"tag {version} does not point at HEAD")

    if github_body_file is not None:
        if not release_note.exists():
            result.error("cannot compare GitHub release body because local release note is missing")
        else:
            body_path = Path(github_body_file)
            if not body_path.is_absolute():
                body_path = root_path / body_path
            if not body_path.exists():
                result.error(f"GitHub release body file missing: {body_path}")
            elif _normalize_body(release_note.read_text(encoding="utf-8")) != _normalize_body(body_path.read_text(encoding="utf-8")):
                result.error("GitHub release body file differs from local release note")

    return result


def _normalize_body(value: str) -> str:
    lines = [line.rstrip() for line in value.strip().splitlines()]
    return "\n".join(lines) + "\n"


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate release note, README latest link, and git tag consistency.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Run release preflight checks.")
    validate.add_argument("version", help="Release version, e.g. v1.1.0.")
    validate.add_argument("--root", type=Path, default=Path("."), help="Repository root.")
    validate.add_argument("--require-tag-at-head", action="store_true", help="Require the tag to point at current HEAD.")
    validate.add_argument("--github-body-file", type=Path, help="Compare an exported GitHub release body to the local release note.")
    validate.add_argument("--quiet", action="store_true", help="Only use exit status.")
    validate.set_defaults(func=_run_validate)

    body = subparsers.add_parser("body", help="Print the local release note body for GitHub release creation.")
    body.add_argument("version")
    body.add_argument("--root", type=Path, default=Path("."), help="Repository root.")
    body.set_defaults(func=_run_body)
    return parser


def _run_validate(args: argparse.Namespace) -> int:
    result = validate_release(
        args.version,
        root=args.root,
        require_tag_at_head=args.require_tag_at_head,
        github_body_file=args.github_body_file,
    )
    if not args.quiet:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    return 0 if result.valid else 1


def _run_body(args: argparse.Namespace) -> int:
    if not VERSION_RE.match(args.version):
        print(f"version must look like vX.Y.Z, got {args.version!r}", file=sys.stderr)
        return 1
    release_note = args.root / "docs" / "releases" / f"{args.version}.md"
    if not release_note.exists():
        print(f"release note missing: {release_note}", file=sys.stderr)
        return 1
    print(release_note.read_text(encoding="utf-8"))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
