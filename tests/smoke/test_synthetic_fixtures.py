from pathlib import Path

from mem.governance.schemas import ManifestRecord, SourceMetadata


def test_synthetic_metadata_fixture_exists() -> None:
    path = Path("tests/fixtures/synthetic/SOURCE_METADATA.json")
    assert path.exists()
    SourceMetadata.model_validate_json(path.read_text(encoding="utf-8"))


def test_synthetic_manifest_record() -> None:
    record = ManifestRecord(
        record_id="syn-001",
        dataset_name="synthetic_stage0",
        dataset_version="0.0.1",
        is_synthetic=True,
        synthetic_recipe_id="stage0-grid",
        disease_label=None,
    )
    assert record.is_synthetic is True
    assert record.disease_label is None
