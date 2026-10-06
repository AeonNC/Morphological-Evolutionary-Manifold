"""Lightweight integration: unapproved provenance cannot reach a split lock."""

from pathlib import Path

import pytest

from mem.governance.fail_closed import FailClosedError
from mem.governance.provenance import load_source_metadata
from mem.governance.schemas import SourceMetadata, SplitLock


def test_unapproved_source_cannot_lock_split(tmp_path: Path) -> None:
    meta = SourceMetadata(
        dataset_name="d1",
        dataset_version="1",
        official_source_url="https://example.invalid/d1",
        source_verification_status="approved",
        license="unknown-placeholder",
        citation_requirement="cite-the-source",
        source_integrity_hash=None,
        intended_MEM_use="research fixture",
        prohibited_MEM_use="clinical use",
        approval_status="approved",
    )
    path = tmp_path / "SOURCE_METADATA.json"
    path.write_text(meta.model_dump_json(), encoding="utf-8")
    with pytest.raises(FailClosedError):
        load_source_metadata(path, tmp_path)
    lock = SplitLock(
        manifest_hash="abc",
        split_hash="def",
        dataset_fingerprint_hashes={},
        seed=0,
        group_identifiers=["patient_id"],
        lock_status="unlocked",
    )
    assert lock.lock_status != "locked"
