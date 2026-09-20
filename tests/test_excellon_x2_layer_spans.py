from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from photonx_eda_pcb.copper_solver.barrel import barrel_is_electrical, barrel_layers
from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.pipeline import reconstruct


GERBER_BODY = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.000*%
D10*
X010000Y010000D03*
M02*
"""


def _gerber(file_function: str) -> str:
    return f"%TF.FileFunction,{file_function}*%\n" + GERBER_BODY


def _drill(file_function: str) -> str:
    return (
        "M48\n"
        f"; #@! TF.FileFunction,{file_function}\n"
        "METRIC\n"
        "T01C0.400\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n"
    )


def _write_four_layer_board(tmp_path: Path, drill_function: str) -> None:
    (tmp_path / "top.gbr").write_text(
        _gerber("Copper,L1,Top,Signal"),
        encoding="utf-8",
    )
    (tmp_path / "inner1.gbr").write_text(
        _gerber("Copper,L2,Inr,Signal"),
        encoding="utf-8",
    )
    (tmp_path / "inner2.gbr").write_text(
        _gerber("Copper,L3,Inr,Signal"),
        encoding="utf-8",
    )
    (tmp_path / "bottom.gbr").write_text(
        _gerber("Copper,L4,Bot,Signal"),
        encoding="utf-8",
    )
    (tmp_path / "span.drl").write_text(
        _drill(drill_function),
        encoding="utf-8",
    )


def _span_pad_layers(board, span):
    index = board.object_index()
    return {index[pad_id].layer for pad_id in span["pad_ids"]}


def _net_layer_sets(board):
    index = board.object_index()
    return {
        frozenset(
            index[member].layer
            for member in net.members
            if hasattr(index[member], "layer")
        )
        for net in board.nets
    }


def test_parser_preserves_normalized_x2_layer_span(tmp_path: Path):
    path = tmp_path / "blind.drl"
    path.write_text(
        _drill("Plated,2,1,Blind,Drill"),
        encoding="utf-8",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.drills) == 1
    drill = result.drills[0]
    assert drill.plating == "plated"
    assert drill.x2_layer_span == (1, 2)
    assert drill.x2_span_kind == "blind"
    assert drill.layer_span is None
    assert drill.span_proven is False
    assert {
        item.kind for item in drill.provenance.evidence
    } == {
        "excellon_x2_file_plating",
        "excellon_x2_file_span",
    }


@pytest.mark.parametrize(
    "file_function",
    [
        "Plated,0,2,Blind",
        "Plated,2,2,Blind",
    ],
)
def test_invalid_x2_layer_ordinals_fail_closed(
    tmp_path: Path,
    file_function: str,
):
    path = tmp_path / "invalid.drl"
    path.write_text(_drill(file_function), encoding="utf-8")

    with pytest.raises(ParseError):
        ExcellonParser(strict=True).parse(path)

    permissive = ExcellonParser(strict=False).parse(path)
    assert permissive.drills == []
    assert any(
        item.code == "INVALID_EXCELLON_X2_PLATING"
        for item in permissive.diagnostics
    )


def test_conflicting_x2_file_spans_fail_closed(tmp_path: Path):
    path = tmp_path / "conflict.drl"
    path.write_text(
        "M48\n"
        "; #@! TF.FileFunction,Plated,1,2,Blind\n"
        "; #@! TF.FileFunction,Plated,1,3,Blind\n"
        "METRIC\n"
        "T01C0.400\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n",
        encoding="utf-8",
    )

    with pytest.raises(ParseError, match="layer-span evidence"):
        ExcellonParser(strict=True).parse(path)


def test_x2_blind_span_limits_vertical_connectivity(tmp_path: Path):
    _write_four_layer_board(
        tmp_path,
        "Plated,1,2,Blind,Drill",
    )

    board = reconstruct(tmp_path).board
    assert board.metadata["x2_copper_stackup"]["status"] == "declared"

    span = board.metadata["via_spans"][0]
    assert span["proven"] is True
    assert span["from_layer"] == "F.Cu"
    assert span["to_layer"] == "In1.Cu"
    assert span["layer_ids"] == ["F.Cu", "In1.Cu"]
    assert _span_pad_layers(board, span) == {"F.Cu", "In1.Cu"}
    assert board.drills[0].x2_layer_span == (1, 2)
    assert board.drills[0].layer_span == ("F.Cu", "In1.Cu")
    assert board.drills[0].span_proven is True
    ordered = [NS(name=name) for name in ("F.Cu", "In1.Cu", "In2.Cu", "B.Cu")]
    assert barrel_layers(board.drills[0], ordered) == ["F.Cu", "In1.Cu"]
    assert barrel_is_electrical(board.drills[0]) is True

    assert _net_layer_sets(board) == {
        frozenset({"F.Cu", "In1.Cu"}),
        frozenset({"In2.Cu"}),
        frozenset({"B.Cu"}),
    }


def test_x2_buried_span_connects_only_declared_inner_layers(tmp_path: Path):
    _write_four_layer_board(
        tmp_path,
        "Plated,2,3,Buried,Drill",
    )

    board = reconstruct(tmp_path).board
    span = board.metadata["via_spans"][0]

    assert span["proven"] is True
    assert span["from_layer"] == "In1.Cu"
    assert span["to_layer"] == "In2.Cu"
    assert span["layer_ids"] == ["In1.Cu", "In2.Cu"]
    assert _span_pad_layers(board, span) == {"In1.Cu", "In2.Cu"}
    assert board.drills[0].x2_layer_span == (2, 3)
    assert board.drills[0].layer_span == ("In1.Cu", "In2.Cu")
    assert board.drills[0].span_proven is True

    assert _net_layer_sets(board) == {
        frozenset({"F.Cu"}),
        frozenset({"In1.Cu", "In2.Cu"}),
        frozenset({"B.Cu"}),
    }


def test_x2_span_beyond_declared_stackup_never_falls_back_to_geometry(
    tmp_path: Path,
):
    _write_four_layer_board(
        tmp_path,
        "Plated,1,5,PTH,Drill",
    )

    board = reconstruct(tmp_path).board
    span = board.metadata["via_spans"][0]

    assert span["proven"] is False
    assert span["from_layer"] is None
    assert span["to_layer"] is None
    assert span["layer_ids"] == []
    assert span["pad_ids"] == []
    assert board.drills[0].x2_layer_span == (1, 5)
    assert board.drills[0].layer_span is None
    assert board.drills[0].span_proven is False
    assert len(board.nets) == 4
    assert any(
        item.code == "X2_DRILL_SPAN_UNRESOLVED"
        for item in board.diagnostics
    )


def test_blind_span_without_ordinal_stackup_remains_unresolved(
    tmp_path: Path,
):
    (tmp_path / "top.gtl").write_text(GERBER_BODY, encoding="utf-8")
    (tmp_path / "bottom.gbl").write_text(GERBER_BODY, encoding="utf-8")
    (tmp_path / "blind.drl").write_text(
        _drill("Plated,1,2,Blind,Drill"),
        encoding="utf-8",
    )

    board = reconstruct(tmp_path).board
    span = board.metadata["via_spans"][0]

    assert "x2_copper_stackup" not in board.metadata
    assert span["proven"] is False
    assert span["from_layer"] is None
    assert span["to_layer"] is None
    assert board.drills[0].x2_layer_span == (1, 2)
    assert board.drills[0].layer_span is None
    assert board.drills[0].span_proven is False
    assert len(board.nets) == 2
    assert any(
        item.code == "X2_DRILL_SPAN_UNRESOLVED"
        for item in board.diagnostics
    )


def test_two_layer_pth_span_can_map_without_x2_copper_ordinals(
    tmp_path: Path,
):
    (tmp_path / "top.gtl").write_text(GERBER_BODY, encoding="utf-8")
    (tmp_path / "bottom.gbl").write_text(GERBER_BODY, encoding="utf-8")
    (tmp_path / "through.drl").write_text(
        _drill("Plated,1,2,PTH,Drill"),
        encoding="utf-8",
    )

    board = reconstruct(tmp_path).board
    span = board.metadata["via_spans"][0]

    assert span["proven"] is True
    assert span["from_layer"] == "F.Cu"
    assert span["to_layer"] == "B.Cu"
    assert span["layer_ids"] == ["F.Cu", "B.Cu"]
    assert board.drills[0].layer_span == ("F.Cu", "B.Cu")
    assert board.drills[0].span_proven is True
    assert len(board.nets) == 1



@pytest.mark.parametrize(
    "file_function",
    [
        "Plated,1,2,NPTH,Drill",
        "NonPlated,1,2,PTH,Drill",
    ],
)
def test_x2_plating_and_span_kind_contradictions_fail_closed(
    tmp_path: Path,
    file_function: str,
):
    path = tmp_path / "contradiction.drl"
    path.write_text(_drill(file_function), encoding="utf-8")

    with pytest.raises(ParseError, match="plating/span-kind contradiction"):
        ExcellonParser(strict=True).parse(path)

    permissive = ExcellonParser(strict=False).parse(path)
    assert permissive.drills == []
    assert any(
        item.code == "INVALID_EXCELLON_X2_PLATING"
        for item in permissive.diagnostics
    )
