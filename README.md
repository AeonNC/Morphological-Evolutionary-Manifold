# Morphological Evolutionary Manifold (MEM)

**Morphological Evolutionary Manifold (MEM): A Unified Framework for Clonal Diversity Mapping and Minimal Residual Disease Detection in Leukemia**

Research Use Only. MEM is a computational research framework and is not validated for clinical diagnosis, treatment selection, molecular profiling, clonal lineage reconstruction, or minimal/measurable residual disease reporting.

MEM is **not** a clinical device, **not** a diagnostic system, **not** an MRD assay, and **not** a treatment-decision system.

## Current status

**Stage 0 — governance foundation only.** Modeling, detection, topology, rare-cell experiments, and any research release are **BLOCKED** until later stages are accepted in order.

| Item | Status |
| Stage 0 QMS, fail-closed CLI, claim linter, synthetic fixtures | implemented |
| Dataset adapters and official downloads | not started (Stage 1) |
| YOLO / embeddings / MCDS / Deep SVDD | not started |
| Scientific release | BLOCKED |

## What MEM is allowed to study later

- Image-derived morphology embeddings and computational subpopulation structure.
- Morphological Clonal Diversity Score (MCDS) only as an *exploratory morphology-derived proxy; not molecularly validated*.
- Simulated MRD-style rare-cell detection under controlled low-prevalence conditions, never a clinical MRD result.
- Morphology-associated classification of public AML genetic-entity labels when those labels exist. This is not general molecular diagnostics.

Image-derived subpopulations are **not** genomic clones by default. Cohort-level public genomics resources are **not** patient-linked unless linkage is independently verified.

## Quick start (Stage 0)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[stage0]"
make verify-safety
python -m mem.cli --help
python -m mem.cli claim-lint --output-dir outputs
python -m mem.cli run-redteam --output-dir outputs
python -m mem.cli verify-release --output-dir outputs
```

`verify-release` is expected to exit non-zero at Stage 0.

## Fail-closed rule

If provenance, privacy, leakage, calibration, claim lint, or any listed gate fails, the stage must stop, write `outputs/failures/*.json`, invalidate downstream artifacts, and refuse silent fallbacks.

## Repository map

See `docs/REPOSITORY_TREE.md` and `quality/` for the QMS.

## Citation

See `CITATION.cff`. Do not fabricate performance numbers or biological conclusions.

## License

See `LICENSE`. Dataset licenses are separate and must be recorded in each `SOURCE_METADATA.json`.
