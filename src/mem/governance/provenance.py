"""Provenance and source-metadata validation."""

from __future__ import annotations

from pathlib import Path

from mem.governance.fail_closed import fail
from mem.governance.schemas import SourceMetadata


def load_source_metadata(path: Path, output_dir: Path) -> SourceMetadata:
    if not path.exists():
        fail(
            "MISSING_SOURCE_METADATA",
            f"SOURCE_METADATA.json is missing at {path}",
            repair="Create SOURCE_METADATA.json with all mandatory fields before any training or evaluation.",
            output_dir=output_dir,
            stage="G1",
        )
    import json

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        metadata = SourceMetadata.model_validate(payload)
    except Exception as exc:  # noqa: BLE001
        fail(
            "INVALID_SOURCE_METADATA",
            f"SOURCE_METADATA.json failed schema validation: {exc.__class__.__name__}",
            repair="Correct mandatory fields and re-run validate-provenance.",
            output_dir=output_dir,
            stage="G1",
            details={"path": str(path)},
        )
        raise
    allowed, reason = metadata.may_enter_workflow()
    if not allowed:
        fail(
            "PROVENANCE_UNAPPROVED",
            f"Dataset '{metadata.dataset_name}' may not enter a workflow: {reason}.",
            repair="Complete source verification, license, citation, integrity hash, and approval.",
            output_dir=output_dir,
            stage="G1",
            details={"dataset": metadata.dataset_name, "reason": reason},
        )
    return metadata
