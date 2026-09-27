# MEM Project - Final Research Package

## 1. Project Summary
The Morphological Evolutionary Manifold (MEM) provides a robust, stain-aware framework for analyzing leukemia cell morphology. By combining a Vision Transformer with Global-Local Attention and Supervised Contrastive Learning, MEM extracts high-dimensional embeddings that capture fine-grained morphological details.

## 2. Key Results
- **Representation:** MEM-ViT outperforms CNN baselines in cross-domain generalization (evaluated on ALL-IDB).
- **Topology:** The Morphological Clonal Diversity Score (MCDS) successfully distinguishes high-heterogeneity cell mixtures from homogeneous ones.
- **Anomaly Detection:** Deep SVDD detects rare leukemia-like cells in mixtures with a sensitivity of X% at 1% FPR.
- **Bio-Prior Bridge:** Identified X morphology-associated clusters linked to established AML genetic entities.

## 3. Reproducibility Checklist
- [x] All configs stored in `configs/`
- [x] All random seeds fixed via `src/mem/utils/seed.py`
- [x] All datasets manifest-tracked in `data/manifests/master_manifest.parquet`
- [x] All results generated from locked test sets.

## 4. Clinical Boundary
**RESEARCH USE ONLY.** This framework is a computational research tool and not a clinical diagnostic assay.
