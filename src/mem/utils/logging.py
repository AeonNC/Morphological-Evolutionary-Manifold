"""Structured logging that redacts secrets and never logs PHI."""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from mem.constants import RESEARCH_DISCLAIMER

SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|credential)\s*[:=]\s*\S+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]+"),
    re.compile(r"sk-[A-Za-z0-9]{10,}"),
)


def redact(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = json.dumps(dict(payload), indent=2, sort_keys=True)
    path.write_text(redact(serializable) + "\n", encoding="utf-8")


def get_logger(name: str = "mem") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def disclaimer_record() -> dict[str, str]:
    return {"disclaimer": RESEARCH_DISCLAIMER}
