"""Artifact registry with hash verification."""

from __future__ import annotations

from pathlib import Path

from mem.governance.fail_closed import fail
from mem.governance.schemas import ArtifactRecord
from mem.utils.hashing import sha256_file
from mem.utils.logging import write_json


class ArtifactRegistry:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.records: dict[str, ArtifactRecord] = {}

    def register(self, artifact_id: str, file_path: Path, run_id: str) -> ArtifactRecord:
        record = ArtifactRecord(
            artifact_id=artifact_id,
            path=str(file_path),
            sha256=sha256_file(file_path),
            produced_by_run=run_id,
        )
        self.records[artifact_id] = record
        return record

    def verify(self, artifact_id: str, output_dir: Path) -> None:
        record = self.records.get(artifact_id)
        if record is None:
            fail(
                "ARTIFACT_MISSING",
                f"Artifact '{artifact_id}' is not registered.",
                repair="Re-run the producing stage and register the artifact.",
                output_dir=output_dir,
                stage="G9",
            )
        current = sha256_file(Path(record.path))
        if current != record.sha256:
            record.valid = False
            fail(
                "ARTIFACT_HASH_MISMATCH",
                f"Artifact '{artifact_id}' hash mismatch.",
                repair="Treat the artifact as invalid, re-run the producing stage, and register a new hash.",
                output_dir=output_dir,
                stage="G9",
                details={"expected": record.sha256, "observed": current},
            )

    def save(self) -> None:
        write_json(
            self.path,
            {key: record.model_dump(mode="json") for key, record in self.records.items()},
        )
