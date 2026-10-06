"""Canonical research-only constants for MEM.

Research Use Only. MEM is a computational research framework and is not validated
for clinical diagnosis, treatment selection, molecular profiling, clonal lineage
reconstruction, or minimal/measurable residual disease reporting.
"""

from __future__ import annotations

RESEARCH_DISCLAIMER = (
    "Research Use Only. MEM is a computational research framework and is not "
    "validated for clinical diagnosis, treatment selection, molecular profiling, "
    "clonal lineage reconstruction, or minimal/measurable residual disease reporting."
)

PROJECT_TITLE = (
    "Morphological Evolutionary Manifold (MEM): "
    "A Unified Framework for Clonal Diversity Mapping and "
    "Minimal Residual Disease Detection in Leukemia"
)

PROJECT_SHORT_NAME = "MEM"
PROJECT_VERSION = "0.1.0-stage0"

MCDS_REQUIRED_STATEMENT = "Exploratory morphology-derived proxy; not molecularly validated."

TOPOLOGY_REQUIRED_LIMITATION = (
    "Topology-derived morphology subpopulations are computational descriptors of "
    "embedding structure. They are not genomic clones or phylogenetic lineages "
    "without paired molecular validation."
)

AML_GENETIC_ENTITY_ALLOWED_PHRASE = (
    "morphology-associated classification of public AML genetic-entity labels"
)

PERMITTED_RARE_CELL_LABELS = (
    "rare leukemia-like cell detection",
    "low-prevalence abnormal-cell screening",
    "simulated MRD-style detection",
    "simulated MRD-style rare-cell detection",
    "rare leukemia-like cell detection under controlled low-prevalence conditions",
)

UPLOAD_WARNING = "Do not upload patient-identifiable or clinical data."

INVALID_REPORT_WATERMARK = "INVALID FOR FINAL RESEARCH REPORTING — REQUIREMENTS NOT MET"

PUBLIC_RESEARCH_MODE = "public_research_only"

PROTECTED_SPLIT_HIERARCHY = (
    "patient_id",
    "subject_id",
    "specimen_id",
    "slide_id",
    "parent_image_id",
    "duplicate_cluster_id",
    "near_duplicate_cluster_id",
    "image_id",
)

GATE_ORDER = (
    "G0",
    "G1",
    "G2",
    "G3",
    "G4",
    "G5",
    "G6",
    "G7",
    "G8",
    "G9",
    "G10",
)

ABSTENTION_STATES = (
    "accepted_for_research_scoring",
    "abstain_low_quality",
    "abstain_out_of_distribution",
    "abstain_high_uncertainty",
    "abstain_domain_shift",
    "rejected_invalid_input",
    "rejected_privacy_risk",
    "rejected_provenance_failure",
)

RELEASE_STATUSES = ("PASS", "PASS WITH DOCUMENTED LIMITATIONS", "BLOCKED")

DEGRADED_RUN_STATES = (
    "degraded",
    "invalid",
    "unverified",
    "stale",
    "leaked",
    "uncalibrated",
    "provenance-incomplete",
)
