from mem.governance.fail_closed import FailClosedError, fail
from mem.governance.leakage import audit_protected_group_overlap
import pytest
from pathlib import Path


def test_subject_and_slide_overlap(tmp_path: Path) -> None:
    with pytest.raises(FailClosedError):
        audit_protected_group_overlap(
            [{"subject_id": "S1", "split": "train"}, {"subject_id": "S1", "split": "val"}],
            tmp_path,
        )
    with pytest.raises(FailClosedError):
        audit_protected_group_overlap(
            [{"slide_id": "SL1", "split": "train"}, {"slide_id": "SL1", "split": "test"}],
            tmp_path,
        )


def test_exclusive_groups_pass(tmp_path: Path) -> None:
    overlaps = audit_protected_group_overlap(
        [
            {"patient_id": "P1", "split": "train"},
            {"patient_id": "P2", "split": "test"},
        ],
        tmp_path,
    )
    assert overlaps == {}
