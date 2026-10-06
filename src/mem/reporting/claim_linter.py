"""Scientific claim linter.

Fails reports and releases if prohibited clinical, genomic-clone, or MRD-assay
claims appear without an evidence-linked exception.
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from mem.constants import RESEARCH_DISCLAIMER
from mem.governance.fail_closed import fail
from mem.utils.logging import utc_now_iso, write_json

SCAN_SUFFIXES = {".md", ".py", ".html", ".htm", ".txt", ".yaml", ".yml", ".csv", ".json", ".ipynb"}

SAFE_PHRASES = (
    RESEARCH_DISCLAIMER,
    "Exploratory morphology-derived proxy; not molecularly validated.",
    "Topology-derived morphology subpopulations are computational descriptors of embedding structure. They are not genomic clones or phylogenetic lineages without paired molecular validation.",
    "simulated MRD-style rare-cell detection",
    "simulated MRD-style detection",
    "rare leukemia-like cell detection under controlled low-prevalence conditions",
    "rare leukemia-like cell detection",
    "low-prevalence abnormal-cell screening",
    "morphology-associated classification of public AML genetic-entity labels",
    "INVALID FOR FINAL RESEARCH REPORTING — REQUIREMENTS NOT MET",
    "Do not upload patient-identifiable or clinical data.",
    "not a clinical device",
    "not a diagnostic system",
    "not an MRD assay",
    "not a treatment-decision system",
)

# Phrases that are prohibited unless an explicit evidence-linked exception exists.
PROHIBITED_PATTERNS = (
    ("MRD_POSITIVE", re.compile(r"\bMRD-positive\b", re.I)),
    ("MRD_NEGATIVE", re.compile(r"\bMRD-negative\b", re.I)),
    ("CLINICAL_MRD_RESULT", re.compile(r"\bclinical MRD result\b", re.I)),
    ("CLINICAL_MRD_SENSITIVITY", re.compile(r"\bclinical MRD sensitivity\b", re.I)),
    ("MRD_ASSAY", re.compile(r"\bMRD assay\b", re.I)),
    ("GENOMIC_CLONE", re.compile(r"\bgenomic clones?\b", re.I)),
    ("CLONE_COUNT", re.compile(r"\bclone count\b", re.I)),
    ("PHYLOGENY", re.compile(r"\bphylogeny\b", re.I)),
    ("CLONAL_LINEAGE", re.compile(r"\bclonal lineage\b", re.I)),
    ("CLONAL_EVOLUTION_RECONSTRUCTION", re.compile(r"\bclonal evolution reconstruction\b", re.I)),
    ("MUTATION_DETECTED", re.compile(r"\bmutation detected\b", re.I)),
    ("CLINICAL_DIAGNOSIS_RESULT", re.compile(r"\bclinical diagnosis\b", re.I)),
    ("TREATMENT_RECOMMENDATION", re.compile(r"\btreatment recommendation\b", re.I)),
    ("PROGNOSIS_CLAIM", re.compile(r"\bprognosis\b", re.I)),
    ("DIAGNOSIS_CLAIM", re.compile(r"\bdiagnos(?:is|e[sd]?|tic result)\b", re.I)),
)

NEGATION_WINDOW = re.compile(
    r"(?i)(not |never |no |without |is not |are not |not validated for |blocked |"
    r"must not |do not |research-only|research use only|prohibited|unsupported)"
)

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "outputs",
    ".pytest_cache",
    "node_modules",
}


@dataclass
class ClaimHit:
    path: str
    line: int
    rule_id: str
    excerpt: str
    negated: bool
    exception_id: str | None = None


@dataclass
class LintResult:
    hits: list[ClaimHit] = field(default_factory=list)
    scanned_files: int = 0
    status: str = "PASS"

    @property
    def blocking_hits(self) -> list[ClaimHit]:
        return [hit for hit in self.hits if not hit.negated and hit.exception_id is None]


def _strip_safe_phrases(text: str) -> str:
    cleaned = text
    for phrase in SAFE_PHRASES:
        cleaned = cleaned.replace(phrase, " ")
    return cleaned


def _is_negated(text: str, start: int) -> bool:
    window = text[max(0, start - 120) : start]
    return bool(NEGATION_WINDOW.search(window))


def load_exceptions(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None or not path.exists():
        return {}
    import yaml

    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    exceptions = payload.get("exceptions", {})
    validated: dict[str, dict[str, str]] = {}
    for exception_id, body in exceptions.items():
        if not body.get("evidence_id") or not body.get("rule_id"):
            continue
        validated[str(exception_id)] = {str(k): str(v) for k, v in body.items()}
    return validated


def match_exception(rule_id: str, path: str, exceptions: dict[str, dict[str, str]]) -> str | None:
    for exception_id, body in exceptions.items():
        if body.get("rule_id") != rule_id:
            continue
        scope = body.get("path_glob", "")
        if not scope or Path(path).match(scope) or scope in path.replace("\\", "/"):
            return exception_id
    return None


def scan_text(
    text: str,
    *,
    path: str,
    exceptions: dict[str, dict[str, str]],
) -> list[ClaimHit]:
    hits: list[ClaimHit] = []
    working = _strip_safe_phrases(text)
    for line_no, line in enumerate(working.splitlines(), start=1):
        for rule_id, pattern in PROHIBITED_PATTERNS:
            for match in pattern.finditer(line):
                negated = _is_negated(line, match.start())
                exception_id = match_exception(rule_id, path, exceptions)
                hits.append(
                    ClaimHit(
                        path=path,
                        line=line_no,
                        rule_id=rule_id,
                        excerpt=match.group(0),
                        negated=negated,
                        exception_id=exception_id,
                    )
                )
    return hits


def _notebook_text(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    chunks: list[str] = []
    for cell in payload.get("cells", []):
        source = cell.get("source", [])
        if isinstance(source, list):
            chunks.append("".join(source))
        else:
            chunks.append(str(source))
    return "\n".join(chunks)


def _python_string_literals(path: Path) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    chunks: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            chunks.append(node.value)
    return "\n".join(chunks)


def iter_scan_files(root: Path, *, skip_adversarial: bool = True) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if skip_adversarial and "adversarial" in path.parts:
            continue
        if path.suffix.lower() in SCAN_SUFFIXES:
            yield path


def lint_path(
    root: Path,
    exceptions_path: Path | None = None,
    *,
    skip_adversarial: bool = True,
) -> LintResult:
    exceptions = load_exceptions(exceptions_path)
    result = LintResult()
    target = root if root.is_dir() else root.parent
    files = [root] if root.is_file() else list(iter_scan_files(target, skip_adversarial=skip_adversarial))
    for path in files:
        result.scanned_files += 1
        if path.suffix == ".ipynb":
            text = _notebook_text(path)
        elif path.suffix == ".py":
            text = path.read_text(encoding="utf-8", errors="replace") + "\n" + _python_string_literals(path)
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
        result.hits.extend(scan_text(text, path=str(path), exceptions=exceptions))
    result.status = "FAIL" if result.blocking_hits else "PASS"
    return result


def lint_or_fail(
    root: Path,
    output_dir: Path,
    exceptions_path: Path | None = None,
    allow_draft: bool = False,
) -> LintResult:
    result = lint_path(root, exceptions_path=exceptions_path)
    evidence = {
        "disclaimer": RESEARCH_DISCLAIMER,
        "status": result.status,
        "scanned_files": result.scanned_files,
        "blocking_hits": [hit.__dict__ for hit in result.blocking_hits],
        "negated_or_excepted_hits": [
            hit.__dict__ for hit in result.hits if hit not in result.blocking_hits
        ],
        "timestamp": utc_now_iso(),
    }
    evidence_path = Path(output_dir) / "audits" / "claim_lint.json"
    write_json(evidence_path, evidence)
    if result.status == "FAIL" and not allow_draft:
        fail(
            "CLAIM_LINT_FAIL",
            f"Prohibited unsupported claims found ({len(result.blocking_hits)}).",
            repair=(
                "Remove the prohibited wording, replace with permitted research phrasing, "
                "or register an evidence-linked exception in configs/claims/exceptions.yaml."
            ),
            output_dir=output_dir,
            stage="G9",
            details={"evidence_path": str(evidence_path)},
        )
    return result
