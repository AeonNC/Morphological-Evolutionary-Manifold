"""Research-only Streamlit placeholder. Stage 10 is not accepted."""

from mem.constants import RESEARCH_DISCLAIMER, UPLOAD_WARNING
from mem.governance.fail_closed import refuse_unimplemented
from pathlib import Path


def main() -> None:
    refuse_unimplemented("launch-demo", "10", Path("outputs"))


if __name__ == "__main__":
    print(RESEARCH_DISCLAIMER)
    print(UPLOAD_WARNING)
    main()
