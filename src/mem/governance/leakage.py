"""Leakage and split-lock guards used from Stage 0 onward."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping

from mem.constants import PROTECTED_SPLIT_HIERARCHY
from mem.governance.fail_closed import fail


def audit_protected_group_overlap(
    records: Iterable[Mapping[str, object]],
    output_dir,
    *,
    split_field: str = "split",
) -> dict[str, list[str]]:
    """Fail closed if any protected group identifier appears in more than one split."""
    group_to_splits: dict[str, set[str]] = defaultdict(set)
    for record in records:
        split = str(record.get(split_field) or "")
        if not split:
            continue
        for field in PROTECTED_SPLIT_HIERARCHY:
            value = record.get(field)
            if value in (None, "", "unknown"):
                continue
            group_to_splits[f"{field}:{value}"].add(split)
    overlaps = {key: sorted(splits) for key, splits in group_to_splits.items() if len(splits) > 1}
    if overlaps:
        fail(
            "PROTECTED_GROUP_OVERLAP",
            "Protected-group identifiers appear in more than one split.",
            repair="Rebuild splits so each protected group is exclusive, then create a new SplitLock.",
            output_dir=output_dir,
            stage="G3",
            details={"overlaps": overlaps},
        )
    return overlaps
