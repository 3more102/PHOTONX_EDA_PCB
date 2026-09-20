from pathlib import Path

from photonx_eda_pcb.parsers.manifest import discover_manufacturing_files
from photonx_eda_pcb.pipeline import reconstruct


GERBER_BODY = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.000*%
D10*
X010000Y010000D03*
M02*
"""

EXCELLON_HIT = """M48
METRIC
T01C0.400
%
T01
X1.000Y1.000
M30
"""


def _gerber(file_function: str) -> str:
    return f"%TF.FileFunction,{file_function}*%\n" + GERBER_BODY


def _write_four_layer_partial_package(tmp_path: Path, *, with_drill: bool = False):
    (tmp_path / "top.gbr").write_text(
        _gerber("Copper,L1,Top,Signal"),
        encoding="utf-8",
    )
    (tmp_path / "bottom.gbr").write_text(
        _gerber("Copper,L4,Bot,Signal"),
        encoding="utf-8",
    )
    if with_drill:
        (tmp_path / "board-PTH.drl").write_text(
            EXCELLON_HIT,
            encoding="utf-8",
        )


def test_manifest_preserves_x2_file_function_fields(tmp_path: Path):
    path = tmp_path / "layer.dat"
    path.write_text(
        _gerber("Copper,L3,Inr,Plane"),
        encoding="utf-8",
    )

    files = discover_manufacturing_files(tmp_path)

    assert len(files) == 1
    assert files[0].layer == "In2.Cu"
    assert files[0].x2_file_function == (
        "Copper",
        "L3",
        "Inr",
        "Plane",
    )


def test_x2_bottom_ordinal_declares_missing_inner_copper_layers(tmp_path: Path):
    _write_four_layer_partial_package(tmp_path)

    board = reconstruct(tmp_path).board
    x2 = board.metadata["x2_copper_stackup"]
    stackup = board.metadata["stackup"]

    assert x2["status"] == "declared"
    assert x2["declared_copper_count"] == 4
    assert x2["layers"] == ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]
    assert [
        layer["name"]
        for layer in stackup["layers"]
        if layer["copper"]
    ] == ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]
    assert all(
        layer["source"] == "x2_file_function"
        for layer in stackup["layers"]
        if layer["copper"]
    )
    assert stackup["confidence"] == 0.97
    assert any(
        "4 consecutive physical copper layers" in evidence
        for evidence in stackup["evidence"]
    )


def test_conflicting_x2_bottom_ordinals_fail_closed(tmp_path: Path):
    (tmp_path / "top.gbr").write_text(
        _gerber("Copper,L1,Top"),
        encoding="utf-8",
    )
    (tmp_path / "bottom-a.gbr").write_text(
        _gerber("Copper,L4,Bot"),
        encoding="utf-8",
    )
    (tmp_path / "bottom-b.gbr").write_text(
        _gerber("Copper,L6,Bot"),
        encoding="utf-8",
    )

    board = reconstruct(tmp_path).board
    x2 = board.metadata["x2_copper_stackup"]

    assert x2["status"] == "conflict"
    assert "layers" not in x2
    assert [
        layer["name"]
        for layer in board.metadata["stackup"]["layers"]
        if layer["copper"]
    ] == ["F.Cu", "B.Cu"]
    issues = [
        item
        for item in board.diagnostics
        if item.code == "X2_COPPER_STACKUP_CONFLICT"
    ]
    assert len(issues) == 1
    assert "conflicting X2 bottom copper ordinals" in issues[0].message


def test_x2_declared_stackup_extends_proven_through_via_layer_path(tmp_path: Path):
    _write_four_layer_partial_package(tmp_path, with_drill=True)

    board = reconstruct(tmp_path).board

    assert len(board.drills) == 1
    assert board.drills[0].plating == "plated"
    assert len(board.metadata["via_spans"]) == 1
    span = board.metadata["via_spans"][0]
    assert span["proven"] is True
    assert span["from_layer"] == "F.Cu"
    assert span["to_layer"] == "B.Cu"
    assert span["layer_ids"] == ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]
