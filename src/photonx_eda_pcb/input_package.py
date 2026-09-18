from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import shutil
import tarfile
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

            _safe_target(destination, info.filename)

        zf.extractall(destination)



def _safe_target(destination: Path, member_name: str) -> Path:
    target = (destination / member_name).resolve()
    if target != destination and destination not in target.parents:
        raise ValueError(
            f"unsafe archive member escapes extraction root: {member_name}"
        )
    return target


def _safe_extract_tar(archive: Path, destination: Path) -> None:
    """Extract TAR/TAR.GZ/TGZ without links, devices, or path traversal."""

    destination = destination.resolve()
    total_size = 0

    with tarfile.open(archive, mode="r:*") as tf:
        members = tf.getmembers()
        if len(members) > _MAX_ARCHIVE_FILES:
            raise ValueError(
                f"archive contains {len(members)} entries; "
                f"limit is {_MAX_ARCHIVE_FILES}"
            )

        for info in members:
            _safe_target(destination, info.name)

            if info.issym() or info.islnk():
                raise ValueError(
                    f"archive links are not allowed: {info.name}"
                )
            if info.isdev() or info.isfifo():
                raise ValueError(
                    f"archive special files are not allowed: {info.name}"
                )

            if info.isfile():
                total_size += int(info.size)
                if total_size > _MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                    raise ValueError(
                        "archive expands beyond the PHOTONX safety limit "
                        f"of {_MAX_ARCHIVE_UNCOMPRESSED_BYTES} bytes"
                    )

        for info in members:
            target = _safe_target(destination, info.name)

            if info.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue

            if not info.isfile():
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            source = tf.extractfile(info)
            if source is None:
                raise ValueError(
                    f"could not extract regular archive member: {info.name}"
                )
            with source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


@contextmanager
def prepare_input(source: str | Path):
    """Prepare a directory, manufacturing file, ZIP, TAR, TAR.GZ, or TGZ.

    Archives are extracted into temporary private directories with path
    traversal, entry-count, decompressed-size, and unsafe-member checks. The
    temporary directory remains valid only for the lifetime of this context.
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

    if original.is_file() and tarfile.is_tarfile(original):
        with tempfile.TemporaryDirectory(prefix="photonx-input-") as tmp:
            root = Path(tmp)
            _safe_extract_tar(original, root)
            yield PreparedInput(original=original, root=root, kind="tar")
        return

    if original.is_file():
        yield PreparedInput(original=original, root=original, kind="file")
        return

    raise ValueError(f"unsupported input type: {original}")
