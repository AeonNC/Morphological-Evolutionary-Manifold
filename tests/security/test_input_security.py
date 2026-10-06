from pathlib import Path

import pytest

from mem.governance.fail_closed import FailClosedError
from mem.security.input_validation import (
    assert_safe_relative_path,
    validate_archive_member,
)
from mem.security.secrets import scan_secrets


def test_path_traversal(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    with pytest.raises(FailClosedError):
        assert_safe_relative_path(Path("..") / "escape.png", root, tmp_path)


def test_secret_scan_finds_fake_key(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "config.yaml").write_text('api_key: "sk-abcdefghijklmnopqrstuvwxyz"\n', encoding="utf-8")
    with pytest.raises(FailClosedError):
        scan_secrets(repo, tmp_path, fail_on_hit=True)


def test_archive_absolute_member(tmp_path: Path) -> None:
    with pytest.raises(FailClosedError):
        validate_archive_member("/etc/passwd", 100, tmp_path)
