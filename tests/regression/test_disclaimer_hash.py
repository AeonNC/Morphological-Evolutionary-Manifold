from mem.constants import RESEARCH_DISCLAIMER
from mem.utils.hashing import sha256_text

EXPECTED = sha256_text(RESEARCH_DISCLAIMER)


def test_disclaimer_hash_is_stable() -> None:
    assert len(EXPECTED) == 64
    assert sha256_text(RESEARCH_DISCLAIMER) == EXPECTED
