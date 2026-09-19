from pathlib import Path

import pytest

from photonx_eda_pcb.io.checksums import checksum_manifest
from photonx_eda_pcb.io.discover import (
    discover_manufacturing_files as discover_legacy_files,
)
from photonx_eda_pcb.io.inventory import inventory
from photonx_eda_pcb.io.manifest import build_manifest
from photonx_eda_pcb.io.walk import bounded_regular_files
from photonx_eda_pcb.parsers.manifest import discover_manufacturing_files


def _write_files(root: Path, count: int) -> list[Path]:
    paths = []
    for index in range(count):
        path = root / f"input-{index}.gbr"
        path.write_text("G04 bounded input*\nM02*\n", encoding="utf-8")
        paths.append(path)
    return paths


def test_bounded_regular_files_rejects_oversized_tree(tmp_path: Path):
    _write_files(tmp_path, 3)

    with pytest.raises(ValueError, match="recursive discovery limit of 2 entries"):
        bounded_regular_files(tmp_path, max_entries=2)


def test_recursive_budget_counts_directories_as_entries(tmp_path: Path):
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "board.gbr").write_text("M02*\n", encoding="utf-8")

    with pytest.raises(ValueError, match="recursive discovery limit of 1 entries"):
        bounded_regular_files(tmp_path, max_entries=1)


@pytest.mark.parametrize(
    "operation",
    [
        lambda root: discover_manufacturing_files(root, max_entries=2),
        lambda root: discover_legacy_files(root, max_entries=2),
        lambda root: inventory(root, max_entries=2),
        lambda root: checksum_manifest(root, max_entries=2),
        lambda root: build_manifest(root, max_entries=2),
    ],
)
def test_recursive_input_surfaces_share_entry_budget(tmp_path: Path, operation):
    _write_files(tmp_path, 3)

    with pytest.raises(ValueError, match="recursive discovery limit of 2 entries"):
        operation(tmp_path)


def test_explicit_single_file_does_not_consume_recursive_budget(tmp_path: Path):
    path = tmp_path / "board.gbr"
    path.write_text("%FSLAX24Y24*%\n%MOMM*%\nM02*\n", encoding="utf-8")

    discovered = discover_manufacturing_files(path, max_entries=1)

    assert [item.path for item in discovered] == [path]
