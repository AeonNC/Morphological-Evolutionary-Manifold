from pathlib import Path

from mem.governance.redteam import run_stage0_redteam


def test_stage0_redteam_all_expected_failures(tmp_path: Path) -> None:
    repo = Path(".")
    fixtures = Path("tests/fixtures/adversarial")
    payload = run_stage0_redteam(repo, tmp_path, fixtures)
    assert payload["status"] == "PASS"
    assert payload["failed"] == []
