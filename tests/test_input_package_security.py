from __future__ import annotations

from io import BytesIO
from pathlib import Path
import stat
import tarfile
import zipfile

import pytest

from photonx_eda_pcb import input_package
from photonx_eda_pcb.input_package import (
    _copy_member_bounded,
    _safe_extract_tar,
    _safe_extract_zip,
)


def test_zip_unix_symlink_is_rejected(tmp_path: Path):
    archive = tmp_path / "symlink.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        info = zipfile.ZipInfo("link.gtl")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        zf.writestr(info, "target.gtl")

    with pytest.raises(ValueError, match="archive links are not allowed"):
        _safe_extract_zip(archive, tmp_path / "out")


def test_zip_unix_special_file_is_rejected(tmp_path: Path):
    archive = tmp_path / "fifo.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        info = zipfile.ZipInfo("pipe")
        info.create_system = 3
        info.external_attr = (stat.S_IFIFO | 0o600) << 16
        zf.writestr(info, b"")

    with pytest.raises(ValueError, match="archive special files are not allowed"):
        _safe_extract_zip(archive, tmp_path / "out")


def test_zip_duplicate_normalized_target_is_rejected(tmp_path: Path):
    archive = tmp_path / "duplicate.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("nested/../top.gtl", "first")
        zf.writestr("top.gtl", "second")

    with pytest.raises(ValueError, match="duplicate extraction target"):
        _safe_extract_zip(archive, tmp_path / "out")


def test_zip_file_directory_collision_is_rejected(tmp_path: Path):
    archive = tmp_path / "collision.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("nested/top.gtl", "gerber")
        zf.writestr("nested", "not a directory")

    with pytest.raises(ValueError, match="path type conflict"):
        _safe_extract_zip(archive, tmp_path / "out")


@pytest.mark.parametrize("file_first", [True, False])
def test_zip_parent_file_directory_collision_is_rejected(
    tmp_path: Path,
    file_first: bool,
):
    archive = tmp_path / "parent-collision.zip"
    entries = [
        ("parent", b"file"),
        ("parent/child/", b""),
    ]
    if not file_first:
        entries.reverse()

    with zipfile.ZipFile(archive, "w") as zf:
        for name, payload in entries:
            zf.writestr(name, payload)

    with pytest.raises(ValueError, match="path type conflict"):
        _safe_extract_zip(archive, tmp_path / "out")


def test_tar_duplicate_normalized_target_is_rejected(tmp_path: Path):
    archive = tmp_path / "duplicate.tar"
    with tarfile.open(archive, "w") as tf:
        for name, payload in (
            ("nested/../top.gtl", b"first"),
            ("top.gtl", b"second"),
        ):
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            tf.addfile(info, BytesIO(payload))

    with pytest.raises(ValueError, match="duplicate extraction target"):
        _safe_extract_tar(archive, tmp_path / "out")


@pytest.mark.parametrize("file_first", [True, False])
def test_tar_parent_file_directory_collision_is_rejected(
    tmp_path: Path,
    file_first: bool,
):
    archive = tmp_path / "parent-collision.tar"
    members = ["file", "directory"]
    if not file_first:
        members.reverse()

    with tarfile.open(archive, "w") as tf:
        for kind in members:
            if kind == "file":
                payload = b"file"
                info = tarfile.TarInfo("parent")
                info.size = len(payload)
                tf.addfile(info, BytesIO(payload))
            else:
                info = tarfile.TarInfo("parent/child")
                info.type = tarfile.DIRTYPE
                tf.addfile(info)

    with pytest.raises(ValueError, match="path type conflict"):
        _safe_extract_tar(archive, tmp_path / "out")


def test_stream_copy_enforces_actual_byte_budget():
    source = BytesIO(b"12345")
    output = BytesIO()

    with pytest.raises(ValueError, match="archive expands beyond"):
        _copy_member_bounded(source, output, remaining_bytes=4)

    assert output.getvalue() == b""


def test_stream_copy_rejects_more_bytes_than_member_declares_before_write():
    source = BytesIO(b"12345")
    output = BytesIO()

    with pytest.raises(ValueError, match="member size mismatch"):
        _copy_member_bounded(
            source,
            output,
            remaining_bytes=100,
            expected_bytes=4,
        )

    assert output.getvalue() == b""


def test_stream_copy_rejects_fewer_bytes_than_member_declares():
    source = BytesIO(b"123")
    output = BytesIO()

    with pytest.raises(ValueError, match="member size mismatch"):
        _copy_member_bounded(
            source,
            output,
            remaining_bytes=100,
            expected_bytes=4,
        )

    assert output.getvalue() == b"123"


def test_stream_copy_accepts_exact_member_size():
    source = BytesIO(b"1234")
    output = BytesIO()

    copied = _copy_member_bounded(
        source,
        output,
        remaining_bytes=100,
        expected_bytes=4,
    )

    assert copied == 4
    assert output.getvalue() == b"1234"


def test_zip_member_over_per_file_limit_is_rejected_before_extraction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(input_package, "_MAX_ARCHIVE_MEMBER_BYTES", 4)
    archive = tmp_path / "oversized-member.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("top.gtl", b"12345")

    with pytest.raises(ValueError, match="per-file safety limit"):
        _safe_extract_zip(archive, tmp_path / "out")

    assert not (tmp_path / "out" / "top.gtl").exists()


def test_tar_member_over_per_file_limit_is_rejected_before_extraction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(input_package, "_MAX_ARCHIVE_MEMBER_BYTES", 4)
    archive = tmp_path / "oversized-member.tar"
    payload = b"12345"

    with tarfile.open(archive, "w") as tf:
        info = tarfile.TarInfo("top.gtl")
        info.size = len(payload)
        tf.addfile(info, BytesIO(payload))

    with pytest.raises(ValueError, match="per-file safety limit"):
        _safe_extract_tar(archive, tmp_path / "out")

    assert not (tmp_path / "out" / "top.gtl").exists()


def test_zip_extreme_compression_ratio_is_rejected_before_extraction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(input_package, "_MIN_ZIP_RATIO_CHECK_BYTES", 1)
    monkeypatch.setattr(input_package, "_MAX_ZIP_COMPRESSION_RATIO", 2.0)
    archive = tmp_path / "high-ratio.zip"

    with zipfile.ZipFile(
        archive,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as zf:
        zf.writestr("top.gtl", b"A" * 16_384)

    with pytest.raises(ValueError, match="compression ratio exceeds"):
        _safe_extract_zip(archive, tmp_path / "out")

    assert not (tmp_path / "out" / "top.gtl").exists()


def test_zip_ratio_check_ignores_small_members(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(input_package, "_MIN_ZIP_RATIO_CHECK_BYTES", 1024)
    monkeypatch.setattr(input_package, "_MAX_ZIP_COMPRESSION_RATIO", 1.0)
    archive = tmp_path / "small-member.zip"

    with zipfile.ZipFile(
        archive,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as zf:
        zf.writestr("tiny.gtl", b"A" * 128)

    destination = tmp_path / "out"
    _safe_extract_zip(archive, destination)

    assert (destination / "tiny.gtl").read_bytes() == b"A" * 128
