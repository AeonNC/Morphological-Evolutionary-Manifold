# Colab free-tier strategy

Research Use Only. MEM is a computational research framework and is not validated for clinical diagnosis, treatment selection, molecular profiling, clonal lineage reconstruction, or minimal/measurable residual disease reporting.

Do not upload patient-identifiable or clinical data.

## Stage 0
Use a CPU runtime. Install `requirements-stage0.txt`. Run smoke tests. Do not download TXL-PBC, LMU, C-NMC, or other image corpora yet.

## Later stages (planned)
- GPU when available; expect disconnects.
- Persist hashed artifacts to Drive only after privacy-scan PASS.
- Treat a disconnected session as an incomplete run, never as a partial success.
- Frozen DINOv2 and YOLO weights must be hash-verified before use.
- Free-tier will not support full-scale Gudhi on 1,000-cell bags; enforce runtime caps.

## Limitations
No guaranteed GPU, no guaranteed long jobs, no HIPAA environment, no clinical upload path.
