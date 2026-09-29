# Morphological Evolutionary Manifold (MEM)
## A Unified Framework for Clonal Diversity Mapping and Minimal Residual Disease Detection in Leukemia

“Research Use Only. MEM is a computational research framework and is not validated for clinical diagnosis, treatment selection, molecular profiling, clonal lineage reconstruction, or minimal/measurable residual disease reporting.”

## Overview
MEM is a high-integrity computational hematology research project designed to map morphological diversity in leukemia using advanced representation learning and topological data analysis.

## Core Objectives
1. **Stain-Aware Pipeline:** Quality control, YOLO-based localization, and provenance-preserving extraction.
2. **Robust Embeddings:** ViT-based morphology embeddings using Supervised Contrastive Learning.
3. **Topological Diversity:** Characterizing subpopulations using persistent homology.
4. **Simulated MRD Detection:** Rare-cell anomaly detection using Deep SVDD.
5. **Biological Prior KG:** Linking morphology to public genetic entities.

## Governance & Safety
This project operates under a **Fail Closed** philosophy. No results are reported if any quality gate (Provenance, Privacy, Leakage, Calibration) fails.

## Installation
```bash
pip install -r requirements.txt
```

## Quick Start
```bash
python -m mem.cli setup-colab
```
