"""Stage 0 red-team runner using synthetic fixtures only."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from mem.constants import RESEARCH_DISCLAIMER
from mem.governance.fail_closed import FailClosedError
from mem.governance.leakage import audit_protected_group_overlap
from mem.governance.provenance import load_source_metadata
from mem.privacy.scanner import scan_paths
from mem.reporting.claim_linter import lint_path
from mem.security.input_validation import (
    assert_no_command_metacharacters,
    assert_safe_relative_path,
    validate_archive_member,
    validate_image_file,
)
from mem.security.secrets import assert_pinned_requirement_line, assert_safe_checkpoint, scan_secrets
from mem.utils.logging import write_json

EXPECTED_FAIL = "FAIL_CLOSED"
EXPECTED_PASS = "PASS"


def _expect_fail(fn: Callable[[], None], test_id: str) -> dict[str, str]:
    try:
        fn()
    except FailClosedError as exc:
        return {
            "test_id": test_id,
            "expected": EXPECTED_FAIL,
            "actual": EXPECTED_FAIL,
            "status": "PASS",
            "code": exc.code,
            "artifact": str(exc.artifact_path) if exc.artifact_path else "",
        }
    except SystemExit:
        return {
            "test_id": test_id,
            "expected": EXPECTED_FAIL,
            "actual": EXPECTED_FAIL,
            "status": "PASS",
            "code": "SYSTEM_EXIT",
            "artifact": "",
        }
    return {
        "test_id": test_id,
        "expected": EXPECTED_FAIL,
        "actual": "CONTINUED",
        "status": "FAIL",
        "code": "NO_FAIL_CLOSED",
        "artifact": "",
    }


def run_stage0_redteam(repo_root: Path, output_dir: Path, fixtures: Path) -> dict[str, object]:
    results: list[dict[str, str]] = []

    missing_license = fixtures / "provenance" / "missing_license.json"
    results.append(
        _expect_fail(
            lambda: load_source_metadata(missing_license, output_dir),
            "RT-PROV-MISSING-LICENSE",
        )
    )

    overlap_records = [
        {"patient_id": "P1", "split": "train"},
        {"patient_id": "P1", "split": "test"},
    ]
    results.append(
        _expect_fail(
            lambda: audit_protected_group_overlap(overlap_records, output_dir),
            "RT-LEAK-PATIENT-TRAIN-TEST",
        )
    )

    claim_file = fixtures / "claims" / "prohibited_mrd.md"
    lint = lint_path(claim_file, skip_adversarial=False)
    results.append(
        {
            "test_id": "RT-CLAIM-MRD-POSITIVE",
            "expected": EXPECTED_FAIL,
            "actual": EXPECTED_FAIL if lint.status == "FAIL" else "CONTINUED",
            "status": "PASS" if lint.status == "FAIL" else "FAIL",
            "code": "CLAIM_LINT",
            "artifact": "",
        }
    )

    phi_file = fixtures / "privacy" / "patient_JohnDoe_mrn12345.txt"
    results.append(
        _expect_fail(
            lambda: scan_paths([phi_file], output_dir, fail_on_hit=True),
            "RT-PRIV-FAKE-PHI-FILENAME",
        )
    )

    results.append(
        _expect_fail(
            lambda: assert_no_command_metacharacters("label; rm -rf /", output_dir),
            "RT-SEC-COMMAND-METADATA",
        )
    )
    results.append(
        _expect_fail(
            lambda: assert_safe_relative_path(Path("../escape.png"), fixtures, output_dir),
            "RT-SEC-PATH-TRAVERSAL",
        )
    )
    results.append(
        _expect_fail(
            lambda: validate_archive_member("../evil.py", 10, output_dir),
            "RT-SEC-ARCHIVE-TRAVERSAL",
        )
    )
    results.append(
        _expect_fail(
            lambda: assert_safe_checkpoint(Path("unsafe.pkl"), output_dir),
            "RT-SEC-UNSAFE-CHECKPOINT",
        )
    )
    results.append(
        _expect_fail(
            lambda: assert_pinned_requirement_line("torch>=2.0", output_dir),
            "RT-SEC-UNPINNED-DEP",
        )
    )

    bomb = fixtures / "provenance" / "tiny_invalid.txt"
    if bomb.exists():
        results.append(
            _expect_fail(lambda: validate_image_file(bomb, output_dir), "RT-IMG-INVALID-TYPE")
        )

    failed = [row for row in results if row["status"] != "PASS"]
    payload = {
        "disclaimer": RESEARCH_DISCLAIMER,
        "status": "FAIL" if failed else "PASS",
        "results": results,
        "failed": failed,
        "repo_root": str(repo_root),
    }
    write_json(Path(output_dir) / "control_evidence" / "stage0_redteam.json", payload)
    if failed:
        from mem.governance.fail_closed import fail

        fail(
            "REDTEAM_FAIL",
            f"{len(failed)} Stage 0 red-team tests did not fail closed.",
            repair="Fix the control so the adversarial fixture is rejected, then re-run run-redteam.",
            output_dir=output_dir,
            stage="G0",
            details={"failed": failed},
        )
    return payload
