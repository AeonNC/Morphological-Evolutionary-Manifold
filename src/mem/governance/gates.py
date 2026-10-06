"""Quality gates G0–G10. Later gates cannot bypass earlier failed gates."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from mem.constants import GATE_ORDER, RESEARCH_DISCLAIMER
from mem.governance.fail_closed import FailClosedError, fail
from mem.utils.logging import utc_now_iso, write_json

GATE_TITLES = {
    "G0": "Environment/dependency integrity",
    "G1": "Dataset source/license/provenance/schema approval",
    "G2": "Privacy and input-security approval",
    "G3": "Duplicate, near-duplicate, and split-leakage approval",
    "G4": "Preprocessing and image-QC approval",
    "G5": "Training safety/reproducibility approval",
    "G6": "Performance/calibration/robustness/abstention approval",
    "G7": "Topology stability and claim-scope approval",
    "G8": "Rare-cell mixture/threshold/scope approval",
    "G9": "Report/citation/claim/provenance approval",
    "G10": "Final release checklist approval",
}


@dataclass
class GateRecord:
    gate_id: str
    status: str = "NOT_STARTED"
    evidence_path: str | None = None
    notes: str = ""
    timestamp: str | None = None


@dataclass
class GateRegistry:
    records: dict[str, GateRecord] = field(
        default_factory=lambda: {gate_id: GateRecord(gate_id=gate_id) for gate_id in GATE_ORDER}
    )

    def prior_gates(self, gate_id: str) -> list[str]:
        index = GATE_ORDER.index(gate_id)
        return list(GATE_ORDER[:index])

    def can_start(self, gate_id: str) -> tuple[bool, str]:
        for prior in self.prior_gates(gate_id):
            status = self.records[prior].status
            if status not in {"PASS", "PASS WITH DOCUMENTED LIMITATIONS"}:
                return False, f"Gate {gate_id} blocked because {prior} status is {status}."
        return True, "ok"

    def set_status(
        self,
        gate_id: str,
        status: str,
        *,
        output_dir: Path,
        evidence_path: str | None = None,
        notes: str = "",
        allow_fail: bool = True,
    ) -> GateRecord:
        allowed, reason = self.can_start(gate_id)
        if not allowed and status in {"PASS", "PASS WITH DOCUMENTED LIMITATIONS"}:
            fail(
                "GATE_BYPASS_BLOCKED",
                reason,
                repair="Pass or document limitations for every earlier gate, then re-run this gate.",
                output_dir=output_dir,
                stage=gate_id,
            )
        if status == "FAIL" and not allow_fail:
            raise FailClosedError("GATE_FAIL", "Gate failed.", repair="See evidence.", details={})
        record = self.records[gate_id]
        record.status = status
        record.evidence_path = evidence_path
        record.notes = notes
        record.timestamp = utc_now_iso()
        return record

    def to_dict(self) -> dict[str, Any]:
        return {
            "disclaimer": RESEARCH_DISCLAIMER,
            "gates": {
                gate_id: {
                    "title": GATE_TITLES[gate_id],
                    "status": record.status,
                    "evidence_path": record.evidence_path,
                    "notes": record.notes,
                    "timestamp": record.timestamp,
                }
                for gate_id, record in self.records.items()
            },
        }

    def save(self, path: Path) -> None:
        write_json(path, self.to_dict())

    @classmethod
    def load(cls, path: Path, output_dir: Path) -> "GateRegistry":
        if not path.exists():
            registry = cls()
            registry.save(path)
            return registry
        import json

        payload = json.loads(path.read_text(encoding="utf-8"))
        registry = cls()
        for gate_id, data in payload.get("gates", {}).items():
            if gate_id in registry.records:
                registry.records[gate_id].status = data.get("status", "NOT_STARTED")
                registry.records[gate_id].evidence_path = data.get("evidence_path")
                registry.records[gate_id].notes = data.get("notes", "")
                registry.records[gate_id].timestamp = data.get("timestamp")
        return registry


def evaluate_g0_environment(
    *,
    output_dir: Path,
    python_ok: bool,
    required_modules: Mapping[str, bool],
    unpinned_dependencies: list[str],
) -> dict[str, Any]:
    """Stage 0 environment gate. Training libraries may be absent; that is documented, not bypassed."""
    missing = [name for name, present in required_modules.items() if not present]
    blocking_missing = [name for name in missing if name in {"pydantic", "yaml", "typer", "PIL"}]
    status = "PASS"
    notes: list[str] = []
    if not python_ok:
        fail(
            "PYTHON_VERSION",
            "Python 3.10+ is required.",
            repair="Install Python 3.10 or newer and re-run G0.",
            output_dir=output_dir,
            stage="G0",
        )
    if blocking_missing:
        fail(
            "MISSING_STAGE0_DEPENDENCY",
            f"Stage 0 required modules missing: {blocking_missing}",
            repair="Install Stage 0 dependencies from requirements-stage0.txt and re-run G0.",
            output_dir=output_dir,
            stage="G0",
            details={"missing": blocking_missing},
        )
    if missing:
        status = "PASS WITH DOCUMENTED LIMITATIONS"
        notes.append(f"Optional/later-stage modules not importable: {missing}")
    if unpinned_dependencies:
        fail(
            "UNPINNED_DEPENDENCY",
            f"Unpinned dependencies are not allowed: {unpinned_dependencies}",
            repair="Pin each dependency in requirements.txt / lock metadata and re-run G0.",
            output_dir=output_dir,
            stage="G0",
            details={"unpinned": unpinned_dependencies},
        )
    return {
        "status": status,
        "missing_optional_modules": missing,
        "notes": notes,
        "disclaimer": RESEARCH_DISCLAIMER,
    }
