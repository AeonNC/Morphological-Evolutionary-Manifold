# Morphological Evolutionary Manifold (MEM)
## A Unified Framework for Clonal Diversity Mapping and Minimal Residual Disease Detection in Leukemia

**Research Use Only. MEM is a computational research framework and is not validated for clinical diagnosis, treatment selection, molecular profiling, clonal lineage reconstruction, or minimal/measurable residual disease reporting.**

### Project Overview
MEM is a modular research pipeline designed to analyze leukemia cell morphology. It integrates:
1. **Cell Discovery:** Stain-robust localization and patch extraction.
2. **Representation Learning:** A Vision Transformer with Global-Local Attention and Supervised Contrastive Learning.
3. **Topological Analysis:** Mapping morphological clonal diversity via persistent homology.
4. **Anomaly Detection:** Rare-cell screening for simulated MRD research.
5. **Biological Grounding:** Linking morphological clusters to cohort-level genomic priors.

### Quickstart
1. **Environment Setup:**
   Run `python -m mem.cli setup-colab` in your Google Colab environment.
2. **Data Acquisition:**
   Follow the instructions in `docs/DATA_LICENSES_AND_CITATIONS.md` to acquire datasets.
3. **Baseline Execution:**
   `python -m mem.cli acquire-data --config configs/data/txl_pbc.yaml`
   `python -m mem.cli train-detector --config configs/detector/yolo11n.yaml`

### Reproducibility
All experiments are governed by YAML configurations in the `configs/` directory. Every run saves its resolved configuration, seed, and environment state in `outputs/runs/`.

### Clinical Disclaimer
This framework is intended for computational research and hypothesis generation. It does not provide clinical diagnoses.
