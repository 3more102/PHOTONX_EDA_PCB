from pathlib import Path

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


def _slot(file_function: str) -> str:
    return (
        "M48\n"
        f"; #@! TF.FileFunction,{file_function}\n"
        "METRIC\n"
        "T01C0.800\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000G85X3.000Y1.000\n"
        "M30\n"
    )


def _route(file_function: str) -> str:
    return (
        "M48\n"
        f"; #@! TF.FileFunction,{file_function}\n"
        "METRIC\n"
        "T01C0.800\n"
        "%\n"
        "T01\n"
        "G00X1.000Y1.000\n"
        "M15\n"
        "G01X3.000Y1.000\n"
        "M16\n"
        "M30\n"
    )


def _mixed_geometry(file_function: str) -> str:
    return (
        "M48\n"
        f"; #@! TF.FileFunction,{file_function}\n"
        "METRIC\n"
        "T01C0.800\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000G85X3.000Y1.000\n"
        "G00X1.000Y2.000\n"
        "M15\n"
        "G01X3.000Y2.000\n"
        "M16\n"
        "M30\n"
    )


def _write_four_layer_stackup(tmp_path: Path) -> None:
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


def test_parser_preserves_x2_span_on_g85_slot(tmp_path: Path):
    path = tmp_path / "slot.drl"
    path.write_text(
        _slot("Plated,2,1,Blind,Rout"),
        encoding="utf-8",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.slots) == 1
    slot = result.slots[0]
    assert slot.plated == "plated"
    assert slot.x2_layer_span == (1, 2)
    assert slot.x2_span_kind == "blind"
    assert slot.layer_span is None
    assert slot.span_proven is False
    assert {
        item.kind for item in slot.provenance.evidence
    } == {
        "excellon_x2_file_plating",
        "excellon_x2_file_span",
    }


def test_parser_preserves_x2_span_on_routed_path(tmp_path: Path):
    path = tmp_path / "route.drl"
    path.write_text(
        _route("Plated,3,2,Buried,Rout"),
        encoding="utf-8",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.routes) == 1
    route = result.routes[0]
    assert route.plated == "plated"
    assert route.x2_layer_span == (2, 3)
    assert route.x2_span_kind == "buried"
    assert route.layer_span is None
    assert route.span_proven is False
    assert {
        item.kind for item in route.provenance.evidence
    } == {
        "excellon_x2_file_plating",
        "excellon_x2_file_span",
    }


def test_pipeline_resolves_slot_and_route_against_declared_x2_stackup(
    tmp_path: Path,
):
    _write_four_layer_stackup(tmp_path)
    (tmp_path / "features.drl").write_text(
        _mixed_geometry("Plated,2,3,Buried,Mixed"),
        encoding="utf-8",
    )

    board = reconstruct(tmp_path).board

    assert board.metadata["x2_copper_stackup"]["status"] == "declared"
    assert len(board.slots) == 1
    assert len(board.routes) == 1

    slot = board.slots[0]
    route = board.routes[0]
    for feature in (slot, route):
        assert feature.x2_layer_span == (2, 3)
        assert feature.x2_span_kind == "buried"
        assert feature.layer_span == ("In1.Cu", "In2.Cu")
        assert feature.span_proven is True

    assert not any(
        item.code in {
            "X2_SLOT_SPAN_UNRESOLVED",
            "X2_ROUTE_SPAN_UNRESOLVED",
        }
        for item in board.diagnostics
    )


def test_unmappable_blind_slot_and_route_fail_closed_without_stackup(
    tmp_path: Path,
):
    (tmp_path / "top.gtl").write_text(GERBER_BODY, encoding="utf-8")
    (tmp_path / "bottom.gbl").write_text(GERBER_BODY, encoding="utf-8")
    (tmp_path / "features.drl").write_text(
        _mixed_geometry("Plated,1,2,Blind,Mixed"),
        encoding="utf-8",
    )

    board = reconstruct(tmp_path).board

    assert "x2_copper_stackup" not in board.metadata
    assert len(board.slots) == 1
    assert len(board.routes) == 1

    slot = board.slots[0]
    route = board.routes[0]
    for feature in (slot, route):
        assert feature.x2_layer_span == (1, 2)
        assert feature.x2_span_kind == "blind"
        assert feature.layer_span is None
        assert feature.span_proven is False

    diagnostics = {item.code for item in board.diagnostics}
    assert "X2_SLOT_SPAN_UNRESOLVED" in diagnostics
    assert "X2_ROUTE_SPAN_UNRESOLVED" in diagnostics


def test_two_layer_pth_slot_and_route_use_safe_legacy_mapping(tmp_path: Path):
    (tmp_path / "top.gtl").write_text(GERBER_BODY, encoding="utf-8")
    (tmp_path / "bottom.gbl").write_text(GERBER_BODY, encoding="utf-8")
    (tmp_path / "features.drl").write_text(
        _mixed_geometry("Plated,1,2,PTH,Mixed"),
        encoding="utf-8",
    )

    board = reconstruct(tmp_path).board

    for feature in (*board.slots, *board.routes):
        assert feature.layer_span == ("F.Cu", "B.Cu")
        assert feature.span_proven is True
