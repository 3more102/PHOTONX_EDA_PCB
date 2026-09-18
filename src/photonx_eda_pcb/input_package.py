from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import tempfile
import zipfile


_MAX_ARCHIVE_FILES = 20_000
_MAX_ARCHIVE_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024


@dataclass(frozen=True)
class PreparedInput:
    original: Path
    root: Path
    kind: str


def _safe_extract_zip(archive: Path, destination: Path) -> None:
    destination = destination.resolve()
    total_size = 0

    with zipfile.ZipFile(archive) as zf:
        members = zf.infolist()
        if len(members) > _MAX_ARCHIVE_FILES:
            raise ValueError(
                f"archive contains {len(members)} entries; "
                f"limit is {_MAX_ARCHIVE_FILES}"
            )

        for info in members:
            if info.is_dir():
                continue

            total_size += int(info.file_size)
            if total_size > _MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                raise ValueError(
                    "archive expands beyond the PHOTONX safety limit "
                    f"of {_MAX_ARCHIVE_UNCOMPRESSED_BYTES} bytes"
                )

            target = (destination / info.filename).resolve()
            if target != destination and destination not in target.parents:
                raise ValueError(
                    f"unsafe archive member escapes extraction root: {info.filename}"
                )

        zf.extractall(destination)


@contextmanager
def prepare_input(source: str | Path):
    """Prepare a directory, a single manufacturing file, or a ZIP package.

    ZIP inputs are extracted to a temporary private directory with path-traversal
    and decompressed-size checks. The temporary directory remains valid for the
    lifetime of the context manager only.
    """

    original = Path(source)
    if not original.exists():
        raise FileNotFoundError(original)

    if original.is_dir():
        yield PreparedInput(original=original, root=original, kind="directory")
        return

    if original.is_file() and zipfile.is_zipfile(original):
        with tempfile.TemporaryDirectory(prefix="photonx-input-") as tmp:
            root = Path(tmp)
            _safe_extract_zip(original, root)
            yield PreparedInput(original=original, root=root, kind="zip")
        return

    if original.is_file():
        yield PreparedInput(original=original, root=original, kind="file")
        return

    raise ValueError(f"unsupported input type: {original}")
