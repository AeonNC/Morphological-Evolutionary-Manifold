# Data directory

Research Use Only. MEM is a computational research framework and is not validated for clinical diagnosis, treatment selection, molecular profiling, clonal lineage reconstruction, or minimal/measurable residual disease reporting.

This tree holds local research data. **Do not commit** raw datasets, derived images, PHI, secrets, or large checkpoints.

| Path | Purpose |
| `raw/` | Official downloads plus `SOURCE_METADATA.json` per dataset |
| `interim/` | Audited but not split-locked products |
| `processed/` | Split-locked, hashed products |
| `external/` | Cohort-level public biology tables |
| `manifests/` | `master_manifest.parquet` |
| `quarantine/` | Files that failed provenance, privacy, integrity, or schema checks |

No dataset may enter a workflow until Stage 1 provenance approval. Stage 0 includes only templates and synthetic fixtures under `tests/fixtures/`.
