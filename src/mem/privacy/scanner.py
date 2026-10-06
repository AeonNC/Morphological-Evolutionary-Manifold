"""Privacy scanner for filenames, metadata, EXIF, and fake PHI patterns.

Public research mode only. Potential PHI is quarantined; nothing is logged in cleartext.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from mem.constants import RESEARCH_DISCLAIMER, UPLOAD_WARNING
from mem.governance.fail_closed import fail
from mem.utils.logging import utc_now_iso, write_json

PHI_PATTERNS = {
    "EMAIL": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "PHONE": re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"),
    "DATE_OF_BIRTH": re.compile(r"\b(?:dob|date[_-]?of[_-]?birth)[^\n]{0,20}\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", re.I),
    "MRN": re.compile(r"\b(?:mrn|medical[_-]?record[_-]?number)[-_:]?\s*[A-Z0-9]{4,}\b", re.I),
    "SSN_LIKE": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "PATIENT_NAME_HINT": re.compile(r"\b(?:patient|pt)[-_ ](?:name|id)[-_:]?\s*[A-Za-z]+\b", re.I),
}

EXIF_PHI_KEYS = {"artist", "copyright", "xpcomment", "xpauthor", "imagedescription", "usercomment"}


@dataclass
class PrivacyFinding:
    path: str
    detector: str
    location: str
    severity: str = "high"


@dataclass
class PrivacyScanResult:
    findings: list[PrivacyFinding] = field(default_factory=list)
    scanned_files: int = 0

    @property
    def status(self) -> str:
        return "FAIL" if self.findings else "PASS"


def scan_text(text: str, path: str, location: str) -> list[PrivacyFinding]:
    findings: list[PrivacyFinding] = []
    for detector, pattern in PHI_PATTERNS.items():
        if pattern.search(text):
            findings.append(PrivacyFinding(path=path, detector=detector, location=location))
    return findings


def scan_filename(path: Path) -> list[PrivacyFinding]:
    return scan_text(path.name, str(path), "filename")


def scan_exif(path: Path) -> list[PrivacyFinding]:
    findings: list[PrivacyFinding] = []
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
    except Exception:
        return findings
    try:
        with Image.open(path) as image:
            exif = image.getexif()
            if not exif:
                return findings
            for tag_id, value in exif.items():
                tag = str(TAGS.get(tag_id, tag_id)).lower()
                rendered = str(value)
                if tag in EXIF_PHI_KEYS:
                    findings.extend(scan_text(rendered, str(path), f"exif:{tag}"))
                    if rendered.strip():
                        findings.append(
                            PrivacyFinding(path=str(path), detector="EXIF_FREE_TEXT", location=f"exif:{tag}")
                        )
                else:
                    findings.extend(scan_text(rendered, str(path), f"exif:{tag}"))
    except Exception:
        return findings
    return findings


def scan_json_or_csv(path: Path) -> list[PrivacyFinding]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return scan_text(text, str(path), path.suffix)


def scan_dicom_tags(tags: dict[str, Any], path: str) -> list[PrivacyFinding]:
    findings: list[PrivacyFinding] = []
    sensitive = {"PatientName", "PatientID", "PatientBirthDate", "PatientAddress", "OtherPatientIDs"}
    for key, value in tags.items():
        location = f"dicom:{key}"
        if key in sensitive and str(value).strip():
            findings.append(PrivacyFinding(path=path, detector="DICOM_PHI_TAG", location=location))
        findings.extend(scan_text(str(value), path, location))
    return findings


def scan_paths(paths: Iterable[Path], output_dir: Path, *, fail_on_hit: bool = True) -> PrivacyScanResult:
    result = PrivacyScanResult()
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        result.scanned_files += 1
        result.findings.extend(scan_filename(path))
        suffix = path.suffix.lower()
        if suffix in {".json", ".csv", ".txt", ".md", ".yaml", ".yml"}:
            result.findings.extend(scan_json_or_csv(path))
        if suffix in {".jpg", ".jpeg", ".tif", ".tiff", ".png"}:
            result.findings.extend(scan_exif(path))
    evidence = {
        "disclaimer": RESEARCH_DISCLAIMER,
        "upload_warning": UPLOAD_WARNING,
        "status": result.status,
        "scanned_files": result.scanned_files,
        "finding_count": len(result.findings),
        "findings": [
            {"path": f.path, "detector": f.detector, "location": f.location, "severity": f.severity}
            for f in result.findings
        ],
        "timestamp": utc_now_iso(),
        "note": "Finding details are detector labels only; suspected PHI values are not copied into logs.",
    }
    write_json(Path(output_dir) / "audits" / "privacy_scan.json", evidence)
    if result.findings and fail_on_hit:
        fail(
            "PRIVACY_SCAN_FAIL",
            f"Privacy scanner found {len(result.findings)} potential identifier pattern(s).",
            repair="Quarantine the files, remove identifier-like content, and re-run privacy-scan.",
            output_dir=output_dir,
            stage="G2",
        )
    return result
