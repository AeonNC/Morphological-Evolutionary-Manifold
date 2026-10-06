"""Safe input validation. Fail closed on path traversal, bombs, and unknown types."""

from __future__ import annotations

import mimetypes
from pathlib import Path

from mem.constants import RESEARCH_DISCLAIMER
from mem.governance.fail_closed import fail

ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024
MAX_PIXELS = 40_000_000
MAX_DIMENSION = 10_000
MAX_ARCHIVE_BYTES = 200 * 1024 * 1024


def assert_safe_relative_path(path: Path, root: Path, output_dir: Path) -> None:
    resolved = (root / path).resolve()
    if root.resolve() not in resolved.parents and resolved != root.resolve():
        fail(
            "PATH_TRAVERSAL",
            "Path traversal is not allowed.",
            repair="Use paths that remain inside the declared data root.",
            output_dir=output_dir,
            stage="G2",
            details={"path": str(path)},
        )


def assert_no_command_metacharacters(value: str, output_dir: Path) -> None:
    forbidden = (";", "&&", "|", "`", "$(", "\n")
    if any(token in value for token in forbidden):
        fail(
            "UNSAFE_METADATA_STRING",
            "Metadata contains shell-metacharacter-like tokens and was rejected.",
            repair="Sanitize metadata to alphanumeric, dash, underscore, and space characters.",
            output_dir=output_dir,
            stage="G2",
            details={"disclaimer": RESEARCH_DISCLAIMER},
        )


def validate_image_file(path: Path, output_dir: Path) -> dict[str, int | str]:
    if path.suffix.lower() not in ALLOWED_IMAGE_SUFFIXES:
        fail(
            "INVALID_IMAGE_TYPE",
            f"File suffix {path.suffix} is not an allowed image type.",
            repair="Provide PNG/JPEG/TIFF/BMP research images only.",
            output_dir=output_dir,
            stage="G2",
        )
    size = path.stat().st_size
    if size > MAX_FILE_SIZE_BYTES:
        fail(
            "FILE_TOO_LARGE",
            "File exceeds the maximum allowed size.",
            repair="Reduce the file size or split the archive under the documented limit.",
            output_dir=output_dir,
            stage="G2",
        )
    guessed, _ = mimetypes.guess_type(path.name)
    if guessed and not guessed.startswith("image/"):
        fail(
            "MIME_MISMATCH",
            "MIME guess is not an image type.",
            repair="Inspect the file; only image MIME types are accepted.",
            output_dir=output_dir,
            stage="G2",
        )
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
            if width > MAX_DIMENSION or height > MAX_DIMENSION or width * height > MAX_PIXELS:
                fail(
                    "DECOMPRESSION_BOMB",
                    "Image dimensions exceed safe limits.",
                    repair="Reject the file and quarantine it. Do not open oversized images.",
                    output_dir=output_dir,
                    stage="G2",
                    details={"width": width, "height": height},
                )
            return {"width": width, "height": height, "format": str(image.format)}
    except Exception as exc:  # noqa: BLE001
        fail(
            "CORRUPTED_IMAGE",
            f"Image failed safe decode: {exc.__class__.__name__}",
            repair="Quarantine the file and replace it from the official source.",
            output_dir=output_dir,
            stage="G2",
        )
        raise


def validate_archive_member(name: str, uncompressed_size: int, output_dir: Path) -> None:
    if name.startswith("/") or ".." in Path(name).parts:
        fail(
            "ARCHIVE_PATH_TRAVERSAL",
            "Archive member path is unsafe.",
            repair="Reject the archive; use members confined to a relative directory.",
            output_dir=output_dir,
            stage="G2",
            details={"member": name},
        )
    if uncompressed_size > MAX_ARCHIVE_BYTES:
        fail(
            "ARCHIVE_TOO_LARGE",
            "Archive member exceeds extraction size limit.",
            repair="Reject the archive and request a smaller official distribution.",
            output_dir=output_dir,
            stage="G2",
        )
