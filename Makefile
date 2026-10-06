.PHONY: test lint security-scan privacy-scan redteam claim-lint verify-safety verify-release

PYTHON ?= python

test:
	$(PYTHON) -m pytest tests -q

lint:
	$(PYTHON) -m ruff check src tests scripts

security-scan:
	$(PYTHON) -m mem.cli verify-g0 --output-dir outputs

privacy-scan:
	$(PYTHON) -m mem.cli privacy-scan --output-dir outputs --root tests/fixtures/synthetic

redteam:
	$(PYTHON) -m mem.cli run-redteam --output-dir outputs

claim-lint:
	$(PYTHON) -m mem.cli claim-lint --output-dir outputs --root .

verify-safety:
	$(PYTHON) scripts/verify_safety.py

verify-release:
	$(PYTHON) -m mem.cli verify-release --output-dir outputs
