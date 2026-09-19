from pathlib import Path

import pytest

from photonx_eda_pcb.io.checksums import checksum_manifest
from photonx_eda_pcb.io.discover import (
    discover_manufacturing_files as discover_legacy_files,
)
from photonx_eda_pcb.io.inventory import inventory
from photonx_eda_pcb.io.manifest import build_manifest
from photonx_eda_pcb.parsers.manifest import discover_manufacturing_files


def _symlink_or_skip(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"file symlinks unavailable on this platform: {exc}")


def test_recursive_parser_discovery_skips_file_symlinks(tmp_path: Path):
    real = tmp_path / "real.drl"
    real.write_text(
        "M48\nMETRIC\nT01C0.8\n%\nT01\nX1Y1\nM30\n",
        encoding="utf-8",
    )
    outside = tmp_path.parent / f"{tmp_path.name}-outside.drl"
    outside.write_text(
        "M48\nMETRIC\nT01C0.9\n%\nT01\nX2Y2\nM30\n",
        encoding="utf-8",
    )
    linked = tmp_path / "linked.drl"
    _symlink_or_skip(linked, outside)

    discovered = discover_manufacturing_files(tmp_path)

    assert [item.path for item in discovered] == [real]

    # A directly selected file remains intentional even if its path is a link.
    explicit = discover_manufacturing_files(linked)
    assert [item.path for item in explicit] == [linked]


def test_recursive_io_helpers_skip_file_symlinks(tmp_path: Path):
    real = tmp_path / "real.gbr"
    real.write_text("G04 local*\nM02*\n", encoding="utf-8")
    outside = tmp_path.parent / f"{tmp_path.name}-outside.gbr"
    outside.write_text("G04 outside*\nM02*\n", encoding="utf-8")
    linked = tmp_path / "linked.gbr"
    _symlink_or_skip(linked, outside)

    assert [entry["path"] for entry in inventory(tmp_path)] == ["real.gbr"]
    assert list(checksum_manifest(tmp_path)) == ["real.gbr"]

    discovered = discover_legacy_files(tmp_path)
    assert discovered["gerber"] == [real]
    assert discovered["drill"] == []
    assert discovered["other"] == []

    manifest = build_manifest(tmp_path)
    assert [entry["path"] for entry in manifest["files"]] == ["real.gbr"]
    assert list(manifest["sha256"]) == ["real.gbr"]
