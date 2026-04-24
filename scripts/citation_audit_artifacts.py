"""Project-owned citation-audit artifact resolution helpers.

This module intentionally lives under `scripts/` rather than `citation_auditor/`
because the latter is treated as vendor-coupled until ownership is clarified.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AuditArtifactResolution:
    path: Path | None
    source: str
    message: str
    candidates: tuple[Path, ...] = ()

    @property
    def found(self) -> bool:
        return self.path is not None


def resolve_audit_artifact(
    output_dir: str | Path,
    *,
    session_id: str | None = None,
    explicit_path: str | Path | None = None,
    allow_latest: bool = True,
) -> AuditArtifactResolution:
    """Resolve the aggregated citation-audit JSON for a render run.

    Priority:
      1. explicit `--audit-json`
      2. `output/citation-audit-{session_id}.json`
      3. deprecated `output/citation-audit-latest.json` fallback
    """
    output = Path(output_dir)

    if explicit_path is not None:
        path = Path(explicit_path)
        if path.exists():
            return AuditArtifactResolution(path=path, source="explicit", message=f"Using explicit audit JSON: {path}")
        return AuditArtifactResolution(
            path=None,
            source="explicit-missing",
            message=f"Explicit audit JSON was provided but does not exist: {path}",
            candidates=(path,),
        )

    candidates: list[tuple[str, Path]] = []
    if session_id:
        candidates.append(("session", output / f"citation-audit-{session_id}.json"))
    if allow_latest:
        candidates.append(("latest-fallback", output / "citation-audit-latest.json"))

    for source, candidate in candidates:
        if candidate.exists():
            if source == "latest-fallback":
                return AuditArtifactResolution(
                    path=candidate,
                    source=source,
                    message=f"Using deprecated latest audit JSON fallback: {candidate}",
                    candidates=tuple(path for _, path in candidates),
                )
            return AuditArtifactResolution(
                path=candidate,
                source=source,
                message=f"Using session audit JSON: {candidate}",
                candidates=tuple(path for _, path in candidates),
            )

    return AuditArtifactResolution(
        path=None,
        source="missing",
        message="No citation-audit JSON artifact found.",
        candidates=tuple(path for _, path in candidates),
    )
