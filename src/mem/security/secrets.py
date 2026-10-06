"""Secret and checkpoint safety scanners."""

from __future__ import annotations

import re
from pathlib import Path

from mem.constants import RESEARCH_DISCLAIMER
from mem.governance.fail_closed import fail
from mem.utils.logging import write_json

SECRET_PATTERNS = {
    "API_KEY_ASSIGNMENT": re.compile(r"(?i)(api[_-]?key|secret_key|access_token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    "OPENAI_LIKE": re.compile(r"sk-[A-Za-z0-9]{16,}"),
    "AWS_LIKE": re.compile(r"AKIA[0-9A-Z]{16}"),
}

UNSAFE_CHECKPOINT_SUFFIXES = {".pkl", ".pickle"}


def scan_secrets(root: Path, output_dir: Path, *, fail_on_hit: bool = True) -> dict[str, object]:
    hits: list[dict[str, str]] = []
    skip = {".git", ".venv", "venv", "__pycache__", "outputs"}
    for path in root.rglob("*"):
        if not path.is_file() or any(part in skip for part in path.parts):
            continue
        if path.suffix.lower() not in {".py", ".yaml", ".yml", ".json", ".env", ".txt", ".md", ".toml", ".cfg"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for detector, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                hits.append({"path": str(path), "detector": detector})
    payload = {
        "disclaimer": RESEARCH_DISCLAIMER,
        "status": "FAIL" if hits else "PASS",
        "hit_count": len(hits),
        "hits": hits,
    }
    write_json(Path(output_dir) / "audits" / "secret_scan.json", payload)
    if hits and fail_on_hit:
        fail(
            "SECRET_SCAN_FAIL",
            "Potential secret material was found in the repository tree.",
            repair="Remove the secret, rotate it if it was real, and keep credentials out of git.",
            output_dir=output_dir,
            stage="G0",
        )
    return payload


def assert_safe_checkpoint(path: Path, output_dir: Path) -> None:
    if path.suffix.lower() in UNSAFE_CHECKPOINT_SUFFIXES:
        fail(
            "UNSAFE_CHECKPOINT",
            "Untrusted pickle checkpoints are not allowed.",
            repair="Use a documented, hashed torch/safetensors checkpoint from a registered source.",
            output_dir=output_dir,
            stage="G5",
        )


def assert_pinned_requirement_line(line: str, output_dir: Path) -> None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or stripped.startswith("-"):
        return
    if stripped.startswith("git+") or " @ git+" in stripped:
        fail(
            "UNPINNED_DEPENDENCY",
            f"Unpinned or VCS dependency is not allowed: {stripped}",
            repair="Pin a hashed or version-locked distribution from a trusted index.",
            output_dir=output_dir,
            stage="G0",
        )
    if not any(token in stripped for token in ("==", "===")):
        fail(
            "UNPINNED_DEPENDENCY",
            f"Dependency is not pinned: {stripped}",
            repair="Pin the package with == and record hashes where possible.",
            output_dir=output_dir,
            stage="G0",
        )
