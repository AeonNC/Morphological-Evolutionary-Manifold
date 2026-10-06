"""Run, split, fingerprint, and change-request schemas for Stage 0."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

from mem.constants import RESEARCH_DISCLAIMER


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SourceMetadata(BaseModel):
    dataset_name: str
    dataset_version: str
    official_source_url: str
    mirror_url_if_used: str | None = None
    source_verification_status: Literal["unverified", "approved", "rejected", "pending"]
    download_date: str | None = None
    license: str | None = None
    access_requirements: str | None = None
    redistribution_terms: str | None = None
    citation_requirement: str | None = None
    expected_image_count: int | None = None
    observed_image_count: int | None = None
    expected_label_count: int | None = None
    observed_label_count: int | None = None
    expected_subject_count: int | None = None
    observed_subject_count: int | None = None
    metadata_availability: str | None = None
    source_integrity_hash: str | None = None
    known_limitations: str | None = None
    intended_MEM_use: str
    prohibited_MEM_use: str
    reviewer: str | None = None
    approval_status: Literal["unapproved", "approved", "rejected", "pending"] = "unapproved"
    disclaimer: str = RESEARCH_DISCLAIMER

    def may_enter_workflow(self) -> tuple[bool, str]:
        if self.source_verification_status != "approved":
            return False, "source verification is not approved"
        if not self.license:
            return False, "license is unknown"
        if not self.citation_requirement:
            return False, "citation requirement is unknown"
        if self.approval_status != "approved":
            return False, "data use is not approved"
        if not self.source_integrity_hash:
            return False, "integrity hash is missing"
        return True, "ok"


class ManifestRecord(BaseModel):
    record_id: str
    dataset_name: str
    dataset_version: str
    source_url: str | None = None
    download_date: str | None = None
    license: str | None = None
    citation_required: bool | None = None
    original_file_id: str | None = None
    image_path: str | None = None
    image_sha256: str | None = None
    image_width: int | None = None
    image_height: int | None = None
    image_format: str | None = None
    magnification: str | None = None
    stain_type: str | None = None
    scanner_or_camera: str | None = None
    source_domain: str | None = None
    patient_id: str | None = None
    subject_id: str | None = None
    specimen_id: str | None = None
    slide_id: str | None = None
    field_id: str | None = None
    cell_id: str | None = None
    parent_image_id: str | None = None
    split: str | None = None
    split_group_id: str | None = None
    cell_type_label: str | None = None
    morphology_labels_json: str | None = None
    disease_label: str | None = None
    leukemia_category: str | None = None
    blast_label: str | None = None
    genetic_entity_label: str | None = None
    mutation_label: str | None = None
    fusion_label: str | None = None
    mrd_reference_label: str | None = None
    treatment_timepoint: str | None = None
    is_full_field: bool | None = None
    is_cropped_cell: bool | None = None
    is_synthetic: bool | None = None
    synthetic_recipe_id: str | None = None
    detector_source: str | None = None
    bounding_box_xyxy: str | None = None
    patch_padding: str | None = None
    quality_blur_score: float | None = None
    quality_brightness_score: float | None = None
    quality_saturation_score: float | None = None
    duplicate_cluster_id: str | None = None
    near_duplicate_cluster_id: str | None = None
    data_quality_flag: str | None = None
    annotation_confidence: str | None = None
    notes: str | None = None
    disclaimer: str = RESEARCH_DISCLAIMER


class SplitLock(BaseModel):
    manifest_hash: str
    split_hash: str
    dataset_fingerprint_hashes: dict[str, str]
    seed: int
    group_identifiers: list[str]
    timestamp: datetime = Field(default_factory=_now)
    lock_status: Literal["unlocked", "locked", "invalid"] = "unlocked"
    change_request_reference: str | None = None
    disclaimer: str = RESEARCH_DISCLAIMER


class DatasetFingerprint(BaseModel):
    dataset_name: str
    file_count: int
    content_hash: str
    metadata_hash: str
    timestamp: datetime = Field(default_factory=_now)
    disclaimer: str = RESEARCH_DISCLAIMER


class RunManifest(BaseModel):
    run_id: str
    resolved_config: dict[str, Any]
    manifest_hash: str | None = None
    split_lock_hash: str | None = None
    dataset_fingerprint_hashes: dict[str, str] = Field(default_factory=dict)
    git_commit: str | None = None
    package_versions: dict[str, str] = Field(default_factory=dict)
    cuda_pytorch_versions: dict[str, str] = Field(default_factory=dict)
    gpu_vram: str | None = None
    seed: int | None = None
    command: str
    start_time: datetime = Field(default_factory=_now)
    end_time: datetime | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    predictions_path: str | None = None
    checkpoint_hash: str | None = None
    logs_path: str | None = None
    warnings: list[str] = Field(default_factory=list)
    degraded_state_flag: bool = False
    validation_status: str = "unverified"
    acceptance_status: str = "not_accepted"
    disclaimer: str = RESEARCH_DISCLAIMER


class ChangeRequest(BaseModel):
    change_request_id: str
    reason: str
    impact_analysis: str
    affected_tests: list[str]
    traceability_update_required: bool = True
    new_split_lock_required: bool = False
    status: Literal["draft", "approved", "rejected", "applied"] = "draft"
    disclaimer: str = RESEARCH_DISCLAIMER


class ArtifactRecord(BaseModel):
    artifact_id: str
    path: str
    sha256: str
    produced_by_run: str
    valid: bool = True
    disclaimer: str = RESEARCH_DISCLAIMER
