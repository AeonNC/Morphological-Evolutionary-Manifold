from pathlib import Path

import pytest

from mem.constants import RESEARCH_DISCLAIMER
from mem.governance.fail_closed import FailClosedError, fail
from mem.governance.gates import GateRegistry
from mem.governance.leakage import audit_protected_group_overlap
from mem.governance.provenance import load_source_metadata
from mem.governance.schemas import ManifestRecord, SourceMetadata
from mem.reporting.claim_linter import lint_path, scan_text
from mem.security.input_validation import assert_no_command_metacharacters, validate_archive_member
from mem.security.secrets import assert_pinned_requirement_line, assert_safe_checkpoint


def test_disclaimer_constant() -> None:
    assert RESEARCH_DISCLAIMER.startswith("Research Use Only.")


def test_source_metadata_blocks_unapproved(tmp_path: Path) -> None:
    payload = SourceMetadata(
        dataset_name="synthetic",
        dataset_version="0.0",
        official_source_url="https://example.invalid/synthetic",
        source_verification_status="unverified",
        intended_MEM_use="fixture testing",
        prohibited_MEM_use="any clinical use",
    )
    path = tmp_path / "SOURCE_METADATA.json"
    path.write_text(payload.model_dump_json(indent=2), encoding="utf-8")
    with pytest.raises(FailClosedError) as exc:
        load_source_metadata(path, tmp_path)
    assert exc.value.code == "PROVENANCE_UNAPPROVED"


def test_manifest_allows_null_labels() -> None:
    record = ManifestRecord(
        record_id="r1",
        dataset_name="synthetic",
        dataset_version="0.0",
        blast_label=None,
        mutation_label=None,
        mrd_reference_label=None,
    )
    assert record.blast_label is None
    assert record.mutation_label is None


def test_fail_closed_writes_artifact(tmp_path: Path) -> None:
    with pytest.raises(FailClosedError):
        fail(
            "UNIT_FAIL",
            "intentional failure",
            repair="no repair needed for this unit test",
            output_dir=tmp_path,
            stage="G0",
        )
    artifacts = list((tmp_path / "failures").glob("*.json"))
    assert artifacts


def test_gate_bypass_blocked(tmp_path: Path) -> None:
    registry = GateRegistry()
    with pytest.raises(FailClosedError) as exc:
        registry.set_status("G1", "PASS", output_dir=tmp_path)
    assert exc.value.code == "GATE_BYPASS_BLOCKED"


def test_patient_overlap_fails(tmp_path: Path) -> None:
    records = [
        {"patient_id": "P1", "split": "train"},
        {"patient_id": "P1", "split": "test"},
    ]
    with pytest.raises(FailClosedError) as exc:
        audit_protected_group_overlap(records, tmp_path)
    assert exc.value.code == "PROTECTED_GROUP_OVERLAP"


def test_claim_linter_blocks_mrd_positive() -> None:
    hits = scan_text("The sample is MRD-positive.", path="demo.md", exceptions={})
    blocking = [h for h in hits if not h.negated]
    assert blocking
    assert blocking[0].rule_id == "MRD_POSITIVE"


def test_claim_linter_allows_disclaimer() -> None:
    hits = scan_text(RESEARCH_DISCLAIMER, path="readme.md", exceptions={})
    blocking = [h for h in hits if not h.negated]
    assert blocking == []


def test_claim_linter_allows_negation() -> None:
    hits = scan_text("Never use MRD-positive without a registered exception.", path="policy.md", exceptions={})
    blocking = [h for h in hits if not h.negated]
    assert blocking == []


def test_unpinned_dependency(tmp_path: Path) -> None:
    with pytest.raises(FailClosedError):
        assert_pinned_requirement_line("torch>=2.0", tmp_path)


def test_unsafe_checkpoint(tmp_path: Path) -> None:
    with pytest.raises(FailClosedError):
        assert_safe_checkpoint(Path("model.pkl"), tmp_path)


def test_archive_traversal(tmp_path: Path) -> None:
    with pytest.raises(FailClosedError):
        validate_archive_member("../x.py", 12, tmp_path)


def test_command_injection_metadata(tmp_path: Path) -> None:
    with pytest.raises(FailClosedError):
        assert_no_command_metacharacters("x && reboot", tmp_path)


def test_lint_skips_adversarial_by_default(tmp_path: Path) -> None:
    adv = tmp_path / "adversarial"
    adv.mkdir()
    (adv / "bad.md").write_text("MRD-positive\n", encoding="utf-8")
    result = lint_path(tmp_path, skip_adversarial=True)
    assert result.status == "PASS"
    result2 = lint_path(adv / "bad.md", skip_adversarial=False)
    assert result2.status == "FAIL"
