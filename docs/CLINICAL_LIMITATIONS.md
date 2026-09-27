# Clinical and Scientific Limitations of MEM

**Mandatory Disclaimer:**
Research Use Only. MEM is a computational research framework and is not validated for clinical diagnosis, treatment selection, molecular profiling, clonal lineage reconstruction, or minimal/measurable residual disease reporting.

## 1. Morphological vs. Genomic Clonality
In the context of this project, **"Clonal Diversity Mapping"** refers specifically to the topology- and graph-based characterization of distinct morphological subpopulations within a learned embedding space.

**Critical Distinction:**
Morphology-derived subpopulations are **computational descriptors** of embedding structure. They are **NOT** equivalent to genomic clones or phylogenetic lineages unless independently validated against paired molecular clonal ground truth (e.g., scDNA-seq).

## 2. Simulated vs. Clinical MRD
In the context of this project, **"MRD Detection"** refers to rare-cell or low-prevalence leukemia-like cell detection under controlled, simulated, or retrospective experiments.

**Critical Distinction:**
Clinical Measurable Residual Disease (MRD) assessment requires comparison with a reference standard (e.g., multiparameter flow cytometry, qPCR, dPCR, or error-corrected NGS) with a limit of detection typically $\le 10^{-3}$. The results produced by MEM are simulated benchmarks and do not establish clinical sensitivity or specificity for patient care.

## 3. Biological Prior Grounding
The **Morphology–Biology Prior Bridge** uses cohort-level data (TCGA, GEO, cBioPortal) to provide biological context.

**Critical Distinction:**
These associations are **cohort-level hypothesis generators**. Unless microscopy images are demonstrably paired with the same patient's genomic records, no patient-specific molecular or mutation predictions are made.

## 4. Deployment Restrictions
The MEM codebase must not be used:
- For the diagnosis of any patient.
- For the monitoring of treatment response in a clinical setting.
- As a replacement for validated hematopathology review.
