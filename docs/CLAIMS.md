# Scientific claims policy

Research Use Only. MEM is a computational research framework and is not validated for clinical diagnosis, treatment selection, molecular profiling, clonal lineage reconstruction, or minimal/measurable residual disease reporting.

Run `python -m mem.cli claim-lint`.

Never emit unsupported MRD-positive or MRD-negative result language.
Never emit genomic clone, clone count, phylogeny, clonal lineage, or clonal evolution reconstruction language unless paired molecular clonality ground truth is registered.
Never emit mutation detected from unpaired images.
Never emit a treatment recommendation or prognosis as a system output.
Never describe this software as producing a clinical diagnosis.

Permitted later-stage phrases include simulated MRD-style rare-cell detection and exploratory morphology-derived proxy; not molecularly validated.
