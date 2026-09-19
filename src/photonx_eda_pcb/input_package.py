from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import stat
import tarfile
import tempfile
import zipfile


_MAX_ARCHIVE_FILES = 20_000
_MAX_ARCHIVE_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024
_COPY_CHUNK_BYTES = 1024 * 1024


@dataclass(frozen=True)
class PreparedInput:
    original: Path
    root: Path
    kind: str


def _safe_target(destination: Path, member_name: str) -> Path:
    target = (destination / member_name).resolve()
    if target != destination and destination not in target.parents:
        raise ValueError(
            f"unsafe archive member escapes extraction root: {member_name}"
        )
    return target


def _claim_archive_target(
    destination: Path,
    member_name: str,
    *,
    is_dir: bool,
    seen_files: set[Path],
    seen_dirs: set[Path],
) -> Path:
    target = _safe_target(destination, member_name)

    if is_dir:
        if target in seen_files:
            raise ValueError(
                f"archive path type conflict at extraction target: {member_name}"
            )
        seen_dirs.add(target)
        return target

    if target in seen_files:
        raise ValueError(
            f"archive contains duplicate extraction target: {member_name}"
        )
    if target in seen_dirs:
        raise ValueError(
            f"archive path type conflict at extraction target: {member_name}"
        )

    for parent in target.parents:
        if parent == destination:
            break
        if parent in seen_files:
            raise ValueError(
                f"archive path type conflict at extraction target: {member_name}"
            )
        seen_dirs.add(parent)

    seen_files.add(target)
    return target


def _copy_member_bounded(source, output, remaining_bytes: int) -> int:
    copied = 0
    while True:
        chunk = source.read(_COPY_CHUNK_BYTES)
        if not chunk:
            break
        copied += len(chunk)
        if copied > remaining_bytes:
            raise ValueError(
                "archive expands beyond the PHOTONX safety limit "
                f"of {_MAX_ARCHIVE_UNCOMPRESSED_BYTES} bytes"
            )
        output.write(chunk)
    return copied


def _validate_zip_member_type(info: zipfile.ZipInfo) -> None:
    if info.flag_bits & 0x1:
        raise ValueError(
            f"encrypted archive members are not supported: {info.filename}"
        )

    if info.create_system != 3:
        return

    mode = (info.external_attr >> 16) & 0xFFFF
    file_type = stat.S_IFMT(mode)

    if stat.S_ISLNK(mode):
        raise ValueError(f"archive links are not allowed: {info.filename}")

    if info.is_dir():
        if file_type not in {0, stat.S_IFDIR}:
            raise ValueError(
                f"archive special files are not allowed: {info.filename}"
            )
        return

    if file_type not in {0, stat.S_IFREG}:
        raise ValueError(
            f"archive special files are not allowed: {info.filename}"
        )


def _safe_extract_zip(archive: Path, destination: Path) -> None:
    destination = destination.resolve()
    declared_total = 0
    seen_files: set[Path] = set()
    seen_dirs: set[Path] = {destination}

    with zipfile.ZipFile(archive) as zf:
        members = zf.infolist()
        if len(members) > _MAX_ARCHIVE_FILES:
            raise ValueError(
                f"archive contains {len(members)} entries; "
                f"limit is {_MAX_ARCHIVE_FILES}"
            )

        planned: list[tuple[zipfile.ZipInfo, Path]] = []
        for info in members:
            _validate_zip_member_type(info)
            target = _claim_archive_target(
                destination,
                info.filename,
                is_dir=info.is_dir(),
                seen_files=seen_files,
                seen_dirs=seen_dirs,
            )

            if not info.is_dir():
                declared_total += int(info.file_size)
                if declared_total > _MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                    raise ValueError(
                        "archive expands beyond the PHOTONX safety limit "
                        f"of {_MAX_ARCHIVE_UNCOMPRESSED_BYTES} bytes"
                    )

            planned.append((info, target))

        extracted_total = 0
        for info, target in planned:
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info, "r") as source, target.open("xb") as output:
                copied = _copy_member_bounded(
                    source,
                    output,
                    _MAX_ARCHIVE_UNCOMPRESSED_BYTES - extracted_total,
                )
            if copied != int(info.file_size):
                raise ValueError(
                    f"archive member size mismatch during extraction: {info.filename}"
                )
            extracted_total += copied


def _safe_extract_tar(archive: Path, destination: Path) -> None:
    """Extract TAR/TAR.GZ/TGZ without links, devices, or path traversal."""

    destination = destination.resolve()
    declared_total = 0
    seen_files: set[Path] = set()
    seen_dirs: set[Path] = {destination}

    with tarfile.open(archive, mode="r:*") as tf:
        members = tf.getmembers()
        if len(members) > _MAX_ARCHIVE_FILES:
            raise ValueError(
                f"archive contains {len(members)} entries; "
                f"limit is {_MAX_ARCHIVE_FILES}"
            )

        planned: list[tuple[tarfile.TarInfo, Path]] = []
        for info in members:
            if info.issym() or info.islnk():
                raise ValueError(
                    f"archive links are not allowed: {info.name}"
                )
            if info.isdev() or info.isfifo():
                raise ValueError(
                    f"archive special files are not allowed: {info.name}"
                )
            if not info.isdir() and not info.isfile():
                raise ValueError(
                    f"archive special files are not allowed: {info.name}"
                )

            target = _claim_archive_target(
                destination,
                info.name,
                is_dir=info.isdir(),
                seen_files=seen_files,
                seen_dirs=seen_dirs,
            )

            if info.isfile():
                declared_total += int(info.size)
                if declared_total > _MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                    raise ValueError(
                        "archive expands beyond the PHOTONX safety limit "
                        f"of {_MAX_ARCHIVE_UNCOMPRESSED_BYTES} bytes"
                    )

            planned.append((info, target))

        extracted_total = 0
        for info, target in planned:
            if info.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            source = tf.extractfile(info)
            if source is None:
                raise ValueError(
                    f"could not extract regular archive member: {info.name}"
                )
            with source, target.open("xb") as output:
                copied = _copy_member_bounded(
                    source,
                    output,
                    _MAX_ARCHIVE_UNCOMPRESSED_BYTES - extracted_total,
                )
            if copied != int(info.size):
                raise ValueError(
                    f"archive member size mismatch during extraction: {info.name}"
                )
            extracted_total += copied


@contextmanager
def prepare_input(source: str | Path):
    """Prepare a directory, manufacturing file, ZIP, TAR, TAR.GZ, or TGZ.

    Archives are extracted into temporary private directories with path
    traversal, entry-count, decompressed-size, duplicate-target, and
    unsafe-member checks. The temporary directory remains valid only for the
    lifetime of this context.
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
