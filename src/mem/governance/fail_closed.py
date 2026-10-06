"""Fail-closed control plane.

If a required check fails, execution stops, a structured artifact is written,
downstream work is marked invalid, and no silent fallback is used.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from mem.constants import DEGRADED_RUN_STATES, INVALID_REPORT_WATERMARK, RESEARCH_DISCLAIMER
from mem.utils.hashing import sha256_text
from mem.utils.logging import get_logger, utc_now_iso, write_json

LOGGER = get_logger("mem.fail_closed")


class FailClosedError(RuntimeError):
    """Raised when a required safety, provenance, or quality check fails."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        repair: str,
        artifact_path: Path | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.repair = repair
        self.artifact_path = artifact_path
        self.details = dict(details or {})


@dataclass
class RunState:
    run_id: str
    status: str = "unverified"
    degraded: bool = False
    invalid: bool = False
    failed_checks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    artifacts: dict[str, str] = field(default_factory=dict)
    downstream_invalid: bool = False

    def mark_invalid(self, check_id: str) -> None:
        self.invalid = True
        self.downstream_invalid = True
        self.status = "invalid"
        if check_id not in self.failed_checks:
            self.failed_checks.append(check_id)

    def mark_degraded(self, warning: str) -> None:
        self.degraded = True
        if self.status not in {"invalid", "blocked"}:
            self.status = "degraded"
        self.warnings.append(warning)

    def may_emit_final_result(self) -> bool:
        if self.invalid or self.degraded or self.downstream_invalid:
            return False
        if self.status in DEGRADED_RUN_STATES or self.status in {"blocked", "unverified"}:
            return False
        return self.status in {"verified", "accepted", "PASS", "PASS WITH DOCUMENTED LIMITATIONS"}


def failure_dir(output_dir: Path) -> Path:
    path = Path(output_dir) / "failures"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_failure_artifact(
    output_dir: Path,
    *,
    code: str,
    message: str,
    repair: str,
    stage: str,
    details: Mapping[str, Any] | None = None,
    run_id: str | None = None,
) -> Path:
    payload = {
        "disclaimer": RESEARCH_DISCLAIMER,
        "code": code,
        "message": message,
        "repair": repair,
        "stage": stage,
        "status": "FAIL",
        "downstream_invalid": True,
        "timestamp": utc_now_iso(),
        "run_id": run_id,
        "details": dict(details or {}),
        "watermark": INVALID_REPORT_WATERMARK,
    }
    payload["artifact_hash"] = sha256_text(json.dumps(payload, sort_keys=True, default=str))
    path = failure_dir(output_dir) / f"{stage}_{code}.json"
    write_json(path, payload)
    LOGGER.error("FAIL-CLOSED %s/%s: %s | repair: %s | artifact: %s", stage, code, message, repair, path)
    return path


def fail(
    code: str,
    message: str,
    *,
    repair: str,
    output_dir: Path,
    stage: str,
    details: Mapping[str, Any] | None = None,
    run_id: str | None = None,
    exit_process: bool = False,
) -> None:
    artifact = write_failure_artifact(
        output_dir,
        code=code,
        message=message,
        repair=repair,
        stage=stage,
        details=details,
        run_id=run_id,
    )
    error = FailClosedError(code, message, repair=repair, artifact_path=artifact, details=details)
    if exit_process:
        raise SystemExit(1) from error
    raise error


def refuse_unimplemented(command: str, stage: str, output_dir: Path) -> None:
    fail(
        "STAGE_NOT_ACCEPTED",
        f"Command '{command}' is not enabled because stage '{stage}' has not been accepted.",
        repair=(
            "Complete the prior-stage acceptance report, re-run the required gates, "
            "and only then enable this command."
        ),
        output_dir=output_dir,
        stage=stage,
        details={"command": command},
    )


def assert_run_may_report(state: RunState, output_dir: Path, stage: str = "G9") -> None:
    if not state.may_emit_final_result():
        fail(
            "FINAL_REPORT_BLOCKED",
            "Final results cannot be emitted from a run that is degraded, invalid, or unverified.",
            repair="Repair the failed checks, re-validate, and produce a new verified run.",
            output_dir=output_dir,
            stage=stage,
            details={"status": state.status, "failed_checks": state.failed_checks},
        )


def require_nonempty(value: Sequence[Any] | None, *, name: str, output_dir: Path, stage: str) -> None:
    if not value:
        fail(
            "EMPTY_REQUIRED_INPUT",
            f"Required input '{name}' is empty.",
            repair=f"Provide a non-empty '{name}' and re-run validation.",
            output_dir=output_dir,
            stage=stage,
        )
