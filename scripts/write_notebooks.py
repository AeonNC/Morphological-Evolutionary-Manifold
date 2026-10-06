import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "notebooks"
root.mkdir(exist_ok=True)
disclaimer = (
    "Research Use Only. MEM is a computational research framework and is not "
    "validated for clinical diagnosis, treatment selection, molecular profiling, "
    "clonal lineage reconstruction, or minimal/measurable residual disease reporting."
)
names = [
    ("00_colab_setup.ipynb", "Colab setup (Stage 0)", "Install requirements-stage0.txt. Do not upload patient-identifiable or clinical data. Modeling commands are blocked."),
    ("01_data_audit.ipynb", "Data audit", "Stage 1. This notebook must not run acquisition until provenance is accepted."),
    ("02_stain_qc.ipynb", "Stain QC", "Stage 2. Blocked until Stage 1 acceptance."),
    ("03_yolo_detection.ipynb", "YOLO detection", "Stage 3. Blocked until Stage 2 acceptance."),
    ("04_wbcatt_pretraining.ipynb", "WBCAtt pretraining", "Stage 4. Blocked."),
    ("05_aml_all_training.ipynb", "AML/ALL training", "Stage 4. Blocked. This notebook must not produce a diagnostic claim."),
    ("06_robustness.ipynb", "Robustness", "Stage 5. Blocked."),
    ("07_topology.ipynb", "Topology", "Stage 6. Topology-derived morphology subpopulations are computational descriptors of embedding structure. They are not genomic clones or phylogenetic lineages without paired molecular validation."),
    ("08_rare_cell_detection.ipynb", "Rare-cell detection", "Stage 7. simulated MRD-style rare-cell detection only. Never use unsupported clinical MRD result language."),
    ("09_biology_graph.ipynb", "Biology graph", "Stage 8. Cohort-level priors only unless patient linkage is verified."),
    ("10_final_reporting.ipynb", "Final reporting", "Stage 9. Reports from degraded runs are invalid."),
]
for fname, title, note in names:
    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [f"# {title}\n\n{disclaimer}\n"],
            },
            {"cell_type": "markdown", "metadata": {}, "source": [note + "\n"]},
            {
                "cell_type": "code",
                "metadata": {},
                "outputs": [],
                "execution_count": None,
                "source": [
                    "from mem.constants import RESEARCH_DISCLAIMER, UPLOAD_WARNING\n",
                    "print(RESEARCH_DISCLAIMER)\n",
                    "print(UPLOAD_WARNING)\n",
                ],
            },
        ],
    }
    (root / fname).write_text(json.dumps(nb, indent=2), encoding="utf-8")
print("notebooks written", len(names))
