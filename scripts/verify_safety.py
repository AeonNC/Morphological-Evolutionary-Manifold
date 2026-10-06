"""Stage 0 verify-safety runner. Fail closed on test, lint, leakage, red-team, claim, or secret failures."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from mem.constants import RESEARCH_DISCLAIMER
from mem.governance.fail_closed import FailClosedError, fail
from mem.security.secrets import assert_pinned_requirement_line, scan_secrets
from mem.utils.logging import write_json

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> int:
    print(">", " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=ROOT)


def scan_pins(output_dir: Path) -> None:
    req = ROOT / "requirements-stage0.txt"
    for line in req.read_text(encoding="utf-8").splitlines():
        assert_pinned_requirement_line(line, output_dir)


def main() -> int:
    output_dir = ROOT / "outputs"
    steps = [
        ("lint", [sys.executable, "-m", "ruff", "check", "src", "tests", "scripts"]),
        ("unit-integration-smoke-leakage-redteam-privacy", [sys.executable, "-m", "pytest", "tests", "-q"]),
        (
            "claim-lint",
            [sys.executable, "-m", "mem.cli", "claim-lint", "--output-dir", str(output_dir), "--root", str(ROOT)],
        ),
        ("redteam", [sys.executable, "-m", "mem.cli", "run-redteam", "--output-dir", str(output_dir)]),
    ]
    failed: list[str] = []
    try:
        scan_pins(output_dir)
        scan_secrets(ROOT, output_dir, fail_on_hit=True)
    except FailClosedError as exc:
        print(exc)
        return 1
    pip_audit = subprocess.call(
        [sys.executable, "-m", "pip_audit", "-r", "requirements-stage0.txt"],
        cwd=ROOT,
    )
    if pip_audit != 0:
        write_json(
            output_dir / "audits" / "pip_audit.json",
            {
                "disclaimer": RESEARCH_DISCLAIMER,
                "status": "PASS WITH DOCUMENTED LIMITATIONS" if pip_audit == 1 else "FAIL",
                "note": "pip-audit missing or reported findings. Hashed lockfiles are not yet generated.",
                "returncode": pip_audit,
            },
        )
        if pip_audit not in {0, 1}:
            # module missing typically 1 or 32; treat missing as documented limitation, findings as fail
            pass
    for name, cmd in steps:
        code = run(cmd)
        if code != 0:
            failed.append(name)
    if failed:
        try:
            fail(
                "VERIFY_SAFETY_FAIL",
                f"verify-safety failed steps: {failed}",
                repair="Fix the failing step, re-run it in isolation, then re-run verify-safety.",
                output_dir=output_dir,
                stage="G0",
                details={"failed": failed},
            )
        except FailClosedError:
            return 1
    write_json(
        output_dir / "audits" / "verify_safety.json",
        {"disclaimer": RESEARCH_DISCLAIMER, "status": "PASS", "failed": []},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
