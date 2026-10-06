from pathlib import Path

from mem.privacy.scanner import scan_filename, scan_text


def test_email_pattern_detected() -> None:
    findings = scan_text("contact  jane.doe@example.com please", path="meta.txt", location="notes")
    assert any(item.detector == "EMAIL" for item in findings)


def test_filename_mrn_detected(tmp_path: Path) -> None:
    path = tmp_path / "patient_Jane_mrn998877.txt"
    path.write_text("synthetic fixture", encoding="utf-8")
    findings = scan_filename(path)
    assert findings
