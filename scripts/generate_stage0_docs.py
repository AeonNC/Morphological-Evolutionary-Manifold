"""Generate Stage 0 QMS markdown, CSVs, gitkeeps, and package inits."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = (
    "Research Use Only. MEM is a computational research framework and is not "
    "validated for clinical diagnosis, treatment selection, molecular profiling, "
    "clonal lineage reconstruction, or minimal/measurable residual disease reporting."
)

RISKS = [
    ("R-DATA-PROV", "data provenance", "Unverified source used in modeling", "acquire/audit", "5", "4", "3"),
    ("R-LIC", "licensing", "Unlicensed data used or redistributed", "acquire", "5", "3", "3"),
    ("R-CORRUPT", "corruption", "Corrupted image silently processed", "image QC", "4", "3", "2"),
    ("R-LABEL-MIS", "label mismatch", "Image-label map is wrong", "manifest", "5", "3", "3"),
    ("R-LABEL-MISS", "missing labels", "Unknown labels treated as negative", "training", "5", "4", "2"),
    ("R-DUP", "duplicates", "Exact duplicates cross splits", "duplicate audit", "4", "4", "2"),
    ("R-NEARDUP", "near duplicates", "Near-duplicates leak test morphology", "near-dup audit", "4", "4", "3"),
    ("R-LEAK-PT", "patient leakage", "Same patient in train and test", "split lock", "5", "3", "2"),
    ("R-LEAK-SUB", "subject leakage", "Same subject in train and test", "split lock", "5", "3", "2"),
    ("R-LEAK-SLIDE", "slide leakage", "Same slide in train and test", "split lock", "5", "3", "2"),
    ("R-LEAK-PATCH", "patch leakage", "Patches from one parent cross splits", "patch extract", "5", "3", "2"),
    ("R-LEAK-PRE", "preprocessing leakage", "Test used for stain/PCA/scaler fit", "preprocess", "5", "3", "2"),
    ("R-LEAK-THR", "threshold leakage", "Threshold chosen on test", "evaluation", "5", "3", "2"),
    ("R-TOPO-MIS", "topology misuse", "Topology treated as genomic clone structure", "topology", "5", "4", "2"),
    ("R-MRD-CLAIM", "MRD overclaim", "Simulated rare-cell work described as an MRD assay", "reporting", "5", "4", "2"),
    ("R-GEN-CLAIM", "genomic overclaim", "Unpaired images used as mutation tests", "reporting", "5", "4", "2"),
    ("R-PRIV", "privacy exposure", "Identifier-like content in files or EXIF", "privacy scan", "5", "2", "2"),
    ("R-SECRET", "secret exposure", "Keys committed to git or logs", "secret scan", "5", "2", "2"),
    ("R-DEP", "dependency compromise", "Unpinned or malicious package", "G0", "5", "2", "3"),
    ("R-CKPT", "model/checkpoint compromise", "Untrusted pickle loaded", "training", "5", "2", "2"),
    ("R-POISON", "data poisoning", "Tampered public mirror", "provenance", "5", "2", "3"),
    ("R-OOD", "OOD input", "Non-blood image scored without abstention", "inference UI", "4", "4", "2"),
    ("R-SHIFT", "domain shift", "Scanner/stain shift ignored", "robustness", "4", "4", "3"),
    ("R-STAIN", "stain confounding", "Stain identity drives predictions", "stain ablation", "4", "4", "3"),
    ("R-IMB", "class imbalance", "Metrics hide minority failure", "evaluation", "4", "4", "2"),
    ("R-CAL", "calibration", "Uncalibrated probabilities exported", "calibration", "4", "3", "2"),
    ("R-FAIR", "fairness", "Subgroup failure unmeasured", "fairness eval", "4", "4", "4"),
    ("R-COLLAPSE", "model collapse", "Deep SVDD or contrastive collapse", "training safety", "4", "3", "2"),
    ("R-TDA", "TDA instability", "Persistent homology unstable to seed/sample", "topology", "4", "4", "3"),
    ("R-STALE", "stale reports", "Report built from old metrics", "report builder", "4", "3", "2"),
    ("R-FAB", "fabricated metrics", "Numbers reported without artifacts", "report builder", "5", "2", "2"),
    ("R-REPRO", "reproducibility failure", "Run cannot be reconstructed", "run manifest", "4", "3", "2"),
    ("R-COLAB", "Colab interruption", "Session dies mid-run", "Colab ops", "3", "4", "3"),
    ("R-LOSS", "artifact loss", "Drive/local artifacts lost", "artifact registry", "3", "3", "3"),
    ("R-UI", "UI automation bias", "Demo looks like a clinical tool", "human factors", "5", "3", "2"),
    ("R-RETRAIN", "unsafe retraining", "Retrain without change control", "change control", "4", "3", "2"),
    ("R-DRIFT", "model drift", "Silent performance change after lock", "monitoring", "4", "3", "3"),
]


def md(title: str, body: str) -> str:
    return f"# {title}\n\n{D}\n\n{body.strip()}\n"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def risk_priority(sev: int, like: int, det: int) -> int:
    return sev * like * (6 - det)


def main() -> None:
    quality = ROOT / "quality"
    docs = {
        "QUALITY_MANUAL.md": md(
            "Quality Manual",
            """
## Purpose
This quality management system (QMS) governs the Morphological Evolutionary Manifold (MEM) research program. MEM is research-only. It is not a clinical device, not a diagnostic system, not an MRD assay, and not a treatment-decision system.

## Scope
Stage 0 through Stage 10 of the MEM repository, including data governance, modeling, topology, simulated rare-cell experiments, reporting, and the research-only Streamlit demonstration.

## Quality policy
1. Fail closed. Never silently substitute a fallback.
2. Do not fabricate data, labels, metrics, citations, or biological conclusions.
3. Do not start a later stage until prior-stage acceptance criteria pass.
4. No final result may be reported from a degraded, invalid, unverified, stale, leaked, uncalibrated, or provenance-incomplete run.

## Organizational roles
Principal Investigator, CSO, computational hematology researcher, medical-AI architect, Python/PyTorch engineer, MLOps engineer, clinical safety officer (research-claim safety, not clinical practice), data governance officer, biostatistician, cybersecurity engineer, QA lead, and independent red-team reviewer. In a thesis setting these roles may be held by the student with named faculty oversight.

## Documents
See the files in `quality/` and SOPs in `quality/STANDARD_OPERATING_PROCEDURES/`.

## Record control
Every run writes a RunManifest. Artifacts are hashed. Reports require claim-lint PASS, locked-test provenance, calibration status, and uncertainty intervals.
""",
        ),
        "RISK_MANAGEMENT_PLAN.md": md(
            "Risk Management Plan",
            """
## Method
Risks are scored as severity (1-5), likelihood (1-5), and detectability (1-5, where 1 is easy to detect). Risk priority number (RPN) = severity × likelihood × (6 − detectability).

## Residual risk policy
Residual risk is accepted only in writing, never by silence. Risks that can produce prohibited scientific claims, leakage, or privacy exposure are release-blocking until mitigated.

## Register
See `quality/RISK_REGISTER.csv`.

## Review
Risks are reviewed at every stage gate and before any research release. Stage 0 residual risks include incomplete dataset access, unhashed dependency lockfiles, and unimplemented later-stage models.
""",
        ),
        "HAZARD_ANALYSIS.md": md(
            "Hazard Analysis",
            """
## Hazardous situations (research program, not clinical use)
| Hazard | Hazardous situation | Harm |
| Unverified public image | Used as if licensed and patient-linked | Invalid thesis/journal claims; possible license violation |
| Split leakage | Test morphology seen in training | Inflated metrics presented as generalization |
| Prohibited wording | Report says an unsupported MRD or genomic-clone claim | Reader believes a clinical or molecular result exists |
| Identifier-like metadata | File names or EXIF contain fake or real identifiers | Privacy incident if real; process failure if fake is missed |
| Untrusted checkpoint | Pickle executed | Code execution |
| Demo UI | Looks like a diagnostic product | User overtrust / automation bias |
| Topology output | Never interpret topology as phylogeny | False biological narrative |

## Controls
Prevention, detection, and fail-closed stop. See the control-evidence matrix.
""",
        ),
        "THREAT_MODEL.md": md(
            "Threat Model",
            """
## Assets
Public research images, manifests, splits, embeddings, checkpoints, reports, secrets, developer workstations, Colab runtimes, GitHub repository.

## Adversaries / failure sources
Honest researcher error, confirmation bias, compromised dependency, poisoned mirror, accidental PHI in a filename, UI overclaim, future unauthorized clinical upload.

## STRIDE-style notes
- Spoofing: fake dataset mirrors. Control: official URL + hash.
- Tampering: altered labels. Control: manifest hashes + duplicate audit.
- Repudiation: unreproducible metrics. Control: RunManifest.
- Information disclosure: secrets/PHI. Control: scanners + quarantine.
- Denial of service: decompression bombs. Control: pixel/size caps.
- Elevation: later gate started after failed earlier gate. Control: GateRegistry.

## Out of scope
Hospital EHR integration, bedside use, and any clinical upload workflow.
""",
        ),
        "DATA_GOVERNANCE_PLAN.md": md(
            "Data Governance Plan",
            """
## Principles
Public research mode only. No dataset enters training/evaluation unless source verification, license, citation, schema, mapping, hashes, duplicate audit, privacy scan, and approval all pass.

## Manifest
`data/manifests/master_manifest.parquet` is the only legal inventory after Stage 1. Missing fields are null. Unknown is never remapped to negative.

## Quarantine
`data/quarantine/` holds corrupted, unlicensed, unknown-label, identifier-like, or dangerous files.

## Forbidden inferences
Never infer missing patient IDs, mutation labels, blast labels, or MRD labels.
""",
        ),
        "PRIVACY_AND_DEIDENTIFICATION.md": md(
            "Privacy and De-identification",
            """
Public datasets are still scanned. Filenames, CSV/JSON, notes, EXIF, and DICOM tags are checked for identifier-like patterns.

Streamlit must not persist uploads by default. Display: Do not upload patient-identifiable or clinical data.

Rejected files are quarantined. Suspected identifier values are not copied into logs.
""",
        ),
        "MODEL_CHANGE_CONTROL.md": md(
            "Model Change Control",
            """
No final result may change after test locking without a ChangeRequest ID, reason, impact analysis, re-run of affected tests, traceability update, and a new SplitLock if splits are affected.

Unsafe retraining without this process is a blocked release condition.
""",
        ),
        "VALIDATION_MASTER_PLAN.md": md(
            "Validation Master Plan",
            """
Gates G0–G10 execute in order. Stage 0 validates the QMS, fail-closed engine, claim linter, synthetic fixtures, and red-team wiring.

Later stages add provenance, leakage, preprocessing, detection, representation learning, topology, simulated rare-cell detection, knowledge graph, reporting, and research-only UI validation.

Never claim clinical validation in this repository.
""",
        ),
        "SOFTWARE_REQUIREMENTS_SPECIFICATION.md": md(
            "Software Requirements Specification",
            """
## Functional
- FR-01 Fail closed on listed safety failures.
- FR-02 Claim linter blocks prohibited unsupported wording.
- FR-03 CLI commands exist for every listed operation; unimplemented stages refuse.
- FR-04 SplitLock and protected-group exclusivity.
- FR-05 Research disclaimer appears in required surfaces.

## Non-functional
- NFR-01 Python 3.10+.
- NFR-02 No secrets or datasets in git.
- NFR-03 CPU smoke tests complete quickly without external download.
- NFR-04 Colab-free-tier first; Drive persistence optional after privacy-scan PASS.
""",
        ),
        "RELEASE_CHECKLIST.md": md(
            "Release Checklist",
            """
A research release may be PASS, PASS WITH DOCUMENTED LIMITATIONS, or BLOCKED.

Stage 0 expected status: BLOCKED for scientific release; Stage 0 governance acceptance may still be recorded separately.

Blockers include leakage, privacy fail, unresolved provenance, failed critical red-team, failed calibration/robustness, test used in development, hash mismatch, prohibited claims, missing uncertainty/provenance, or reports from degraded runs.
""",
        ),
        "INCIDENT_RESPONSE_PLAN.md": md(
            "Incident Response Plan",
            """
1. Stop the affected pipeline.
2. Mark artifacts invalid.
3. Quarantine suspect files.
4. Rotate any exposed credentials.
5. Write an incident record under `outputs/failures/`.
6. Do not silently continue.
""",
        ),
        "MONITORING_AND_DRIFT_PLAN.md": md(
            "Monitoring and Drift Plan",
            """
After a split is locked, metric movement requires a change request. Colab interruption is treated as an incomplete run, not a partial success. Stale reports are invalid.
""",
        ),
        "FAIRNESS_AND_EQUITY_PLAN.md": md(
            "Fairness and Equity Plan",
            """
Evaluate available source/site/scanner/stain/disease metadata. Evaluate demographics only if validated metadata exist. If they do not exist, state that fairness cannot be measured. Do not invent subgroups.
""",
        ),
        "HUMAN_FACTORS_AND_UI_SAFETY.md": md(
            "Human Factors and UI Safety",
            """
The Streamlit app is a research demonstration. Header and footer must show the research disclaimer. No score without uncertainty, input-quality status, OOD status, provenance, and the disclaimer. No clinical upload workflow.
""",
        ),
        "SECURITY_PLAN.md": md(
            "Security Plan",
            """
Controls: extension/MIME checks, safe decode, size/pixel caps, archive validation, path traversal prevention, no untrusted pickle, pin dependencies, SBOM in later stages, secret scan, log redaction, no credentials in repo.
""",
        ),
        "THIRD_PARTY_DEPENDENCY_POLICY.md": md(
            "Third-Party Dependency Policy",
            """
Pin with `==`. Prefer hashed lockfiles (`pip-compile --generate-hashes`) before any research release. Unpinned lines fail G0. VCS installs are rejected. Optional scientific stacks (torch, ultralytics, gudhi) may be absent in Stage 0 CPU environments and must be recorded as documented limitations, not silent fallbacks.
""",
        ),
    }
    for name, text in docs.items():
        write(quality / name, text)

    sop_dir = quality / "STANDARD_OPERATING_PROCEDURES"
    sops = {
        "SOP-01_FAIL_CLOSED.md": "Stop, non-zero exit, structured failure artifact, explain repair, invalidate downstream, quarantine if needed, block training/eval/report/release, no silent fallback, require re-validation.",
        "SOP-02_CLAIM_LINT.md": "Run `python -m mem.cli claim-lint` before reports. Prohibited tokens without negation or evidence-linked exception fail G9.",
        "SOP-03_PRIVACY_SCAN.md": "Run privacy-scan on fixtures in Stage 0 and on acquired data in Stage 1. Quarantine hits.",
        "SOP-04_SPLIT_LOCK.md": "Protected groups are exclusive. Test is immutable. Stage 1 implements locking; Stage 0 only provides the schema and overlap auditor.",
        "SOP-05_REDTEAM.md": "Use synthetic fixtures only. Never corrupt real data. Expected result is reject/quarantine/fail/abstain.",
        "SOP-06_COLAB.md": "Install requirements-stage0.txt. Do not upload patient-identifiable or clinical data. Persist to Drive only after privacy-scan PASS.",
    }
    for name, body in sops.items():
        write(sop_dir / name, md(name.replace(".md", "").replace("_", " "), body))

    # Risk register
    risk_path = quality / "RISK_REGISTER.csv"
    fields = [
        "risk_id",
        "category",
        "threat",
        "affected_process",
        "severity",
        "likelihood",
        "detectability",
        "risk_priority",
        "prevention_control",
        "detection_control",
        "mitigation",
        "residual_risk",
        "owner",
        "evidence_artifact",
        "review_frequency",
        "release_gate",
    ]
    with risk_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for risk_id, category, threat, process, sev, like, det in RISKS:
            rpn = risk_priority(int(sev), int(like), int(det))
            writer.writerow(
                {
                    "risk_id": risk_id,
                    "category": category,
                    "threat": threat,
                    "affected_process": process,
                    "severity": sev,
                    "likelihood": like,
                    "detectability": det,
                    "risk_priority": rpn,
                    "prevention_control": "policy + fail-closed gate",
                    "detection_control": "automated test or scanner",
                    "mitigation": "stop, quarantine, repair, re-validate",
                    "residual_risk": "documented after control evidence exists",
                    "owner": "QA lead / data governance officer",
                    "evidence_artifact": "outputs/control_evidence/",
                    "review_frequency": "each stage gate",
                    "release_gate": "G10",
                }
            )

    # Traceability
    trace_path = quality / "TRACEABILITY_MATRIX.csv"
    tfields = [
        "requirement_id",
        "requirement_text",
        "risk_id",
        "module",
        "implementation_file",
        "test_file",
        "test_id",
        "evidence_artifact",
        "status",
        "reviewer",
        "review_date",
        "change_request_id",
    ]
    traces = [
        ("FR-01", "Fail closed on safety failures", "R-DATA-PROV", "governance", "src/mem/governance/fail_closed.py", "tests/unit/test_governance.py", "test_fail_closed_writes_artifact", "outputs/failures/", "implemented-stage0", "", "", ""),
        ("FR-02", "Claim linter blocks prohibited unsupported wording", "R-MRD-CLAIM", "reporting", "src/mem/reporting/claim_linter.py", "tests/unit/test_governance.py", "test_claim_linter_blocks_mrd_positive", "outputs/audits/claim_lint.json", "implemented-stage0", "", "", ""),
        ("FR-03", "Unimplemented CLI stages refuse", "R-RETRAIN", "cli", "src/mem/cli.py", "tests/smoke/test_cli_smoke.py", "test_later_stage_command_fails_closed", "outputs/failures/", "implemented-stage0", "", "", ""),
        ("FR-04", "Protected-group exclusivity", "R-LEAK-PT", "governance", "src/mem/governance/leakage.py", "tests/leakage/test_split_overlap.py", "test_subject_and_slide_overlap", "outputs/failures/", "implemented-stage0", "", "", ""),
        ("FR-05", "Research disclaimer on CLI help", "R-UI", "cli", "src/mem/cli.py", "tests/smoke/test_cli_smoke.py", "test_help_shows_disclaimer", "n/a", "implemented-stage0", "", "", ""),
        ("FR-06", "Privacy scanner", "R-PRIV", "privacy", "src/mem/privacy/scanner.py", "tests/privacy/test_privacy_scan.py", "test_email_pattern_detected", "outputs/audits/privacy_scan.json", "implemented-stage0", "", "", ""),
        ("FR-07", "Gate order cannot be bypassed", "R-REPRO", "governance", "src/mem/governance/gates.py", "tests/unit/test_governance.py", "test_gate_bypass_blocked", "outputs/audits/gates.json", "implemented-stage0", "", "", ""),
        ("FR-08", "Stage 0 red-team expected failures", "R-FAB", "governance", "src/mem/governance/redteam.py", "tests/redteam/test_stage0_redteam.py", "test_stage0_redteam_all_expected_failures", "outputs/control_evidence/stage0_redteam.json", "implemented-stage0", "", "", ""),
    ]
    with trace_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=tfields)
        writer.writeheader()
        for row in traces:
            writer.writerow(dict(zip(tfields, row)))

    # Control evidence matrix
    cpath = quality / "CONTROL_EVIDENCE_MATRIX.csv"
    cfields = [
        "control_id",
        "risk_id",
        "threat",
        "prevention_control",
        "detection_control",
        "adversarial_test_id",
        "expected_result",
        "actual_result",
        "evidence_path",
        "last_verified",
        "status",
        "release_gate",
        "owner",
        "reviewer",
        "notes",
    ]
    controls = [
        ("C-PROV-LIC", "R-LIC", "missing license", "schema require license", "load_source_metadata", "RT-PROV-MISSING-LICENSE", "FAIL_CLOSED", "pending-runtime", "outputs/control_evidence/stage0_redteam.json", "", "stage0", "G1", "DGO", "", "synthetic only"),
        ("C-LEAK-PT", "R-LEAK-PT", "patient in two splits", "protected hierarchy", "audit_protected_group_overlap", "RT-LEAK-PATIENT-TRAIN-TEST", "FAIL_CLOSED", "pending-runtime", "outputs/control_evidence/stage0_redteam.json", "", "stage0", "G3", "QA", "", ""),
        ("C-CLAIM-MRD", "R-MRD-CLAIM", "unsupported MRD wording", "claim policy", "claim linter", "RT-CLAIM-MRD-POSITIVE", "FAIL_CLOSED", "pending-runtime", "outputs/audits/claim_lint.json", "", "stage0", "G9", "CSO", "", "Never use unsupported MRD-positive wording"),
        ("C-PRIV-FN", "R-PRIV", "identifier-like filename", "public-research mode", "privacy scanner", "RT-PRIV-FAKE-PHI-FILENAME", "FAIL_CLOSED", "pending-runtime", "outputs/audits/privacy_scan.json", "", "stage0", "G2", "privacy", "", "synthetic fixture"),
        ("C-SEC-META", "R-SECRET", "command-like metadata", "input validation", "assert_no_command_metacharacters", "RT-SEC-COMMAND-METADATA", "FAIL_CLOSED", "pending-runtime", "outputs/failures/", "", "stage0", "G2", "security", "", ""),
        ("C-SEC-PATH", "R-POISON", "path traversal", "resolve under root", "assert_safe_relative_path", "RT-SEC-PATH-TRAVERSAL", "FAIL_CLOSED", "pending-runtime", "outputs/failures/", "", "stage0", "G2", "security", "", ""),
        ("C-SEC-ARCH", "R-CORRUPT", "archive traversal", "member path check", "validate_archive_member", "RT-SEC-ARCHIVE-TRAVERSAL", "FAIL_CLOSED", "pending-runtime", "outputs/failures/", "", "stage0", "G2", "security", "", ""),
        ("C-SEC-PKL", "R-CKPT", "pickle checkpoint", "suffix deny", "assert_safe_checkpoint", "RT-SEC-UNSAFE-CHECKPOINT", "FAIL_CLOSED", "pending-runtime", "outputs/failures/", "", "stage0", "G5", "MLOps", "", ""),
        ("C-SEC-PIN", "R-DEP", "unpinned dependency", "pin policy", "assert_pinned_requirement_line", "RT-SEC-UNPINNED-DEP", "FAIL_CLOSED", "pending-runtime", "outputs/failures/", "", "stage0", "G0", "MLOps", "", ""),
        ("C-IMG-TYPE", "R-CORRUPT", "invalid image type", "suffix allow-list", "validate_image_file", "RT-IMG-INVALID-TYPE", "FAIL_CLOSED", "pending-runtime", "outputs/failures/", "", "stage0", "G2", "QA", "", ""),
    ]
    with cpath.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=cfields)
        writer.writeheader()
        for row in controls:
            writer.writerow(dict(zip(cfields, row)))

    # gitkeeps and package inits
    packages = [
        "src/mem/data",
        "src/mem/preprocessing",
        "src/mem/detection",
        "src/mem/models",
        "src/mem/losses",
        "src/mem/training",
        "src/mem/embeddings",
        "src/mem/topology",
        "src/mem/anomaly",
        "src/mem/knowledge_graph",
        "src/mem/evaluation",
        "src/mem/visualization",
        "src/mem/app",
        "src/mem/cli_commands",
        "tests/unit",
        "tests/integration",
        "tests/security",
        "tests/privacy",
        "tests/leakage",
        "tests/redteam",
        "tests/regression",
        "tests/smoke",
    ]
    init_text = f'"""Stage placeholder. {D}"""\n'
    for rel in packages:
        write(ROOT / rel / "__init__.py", init_text)

    keep_dirs = [
        "data/raw",
        "data/interim",
        "data/processed",
        "data/external",
        "data/manifests",
        "data/quarantine",
        "outputs/audits",
        "outputs/failures",
        "outputs/quarantine_reports",
        "outputs/checkpoints",
        "outputs/configs",
        "outputs/embeddings",
        "outputs/predictions",
        "outputs/metrics",
        "outputs/figures",
        "outputs/tables",
        "outputs/reports",
        "outputs/logs",
        "outputs/runs",
        "outputs/control_evidence",
        "assets",
        "configs/data",
        "configs/detector",
        "configs/pretrain",
        "configs/finetune",
        "configs/topology",
        "configs/anomaly",
        "configs/evaluation",
        "configs/demo",
        "scripts",
    ]
    keep_note = (
        "# Keep this directory. Do not commit datasets, PHI, secrets, or large checkpoints.\n"
        f"# {D}\n"
    )
    for rel in keep_dirs:
        write(ROOT / rel / ".gitkeep", keep_note)

    print("stage0 docs generated")


if __name__ == "__main__":
    main()
