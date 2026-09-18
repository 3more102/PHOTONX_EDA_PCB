import pytest

from photonx_eda_pcb.connectivity import build_physical_graph, assign_physical_nets
from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.models import BoardModel, CopperRegion, PadCandidate, Point
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.provenance import Provenance


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text)
    return p


def _region_file(body):
    return "%FSLAX24Y24*%\n%MOMM*%\n" + body + "\nM02*\n"


def test_linear_dark_region_is_reconstructed_with_provenance(tmp_path):
    p = _write(
        tmp_path,
        "region.gbr",
        _region_file(
            "G36*\n"
            "X000000Y000000D02*\n"
            "X020000Y000000D01*\n"
            "X020000Y010000D01*\n"
            "X000000Y010000D01*\n"
            "X000000Y000000D01*\n"
            "G37*"
        ),
    )

    result = GerberRS274XParser("F.Cu").parse(p)

    assert not result.tracks
    assert not result.pads
    assert len(result.regions) == 1
    region = result.regions[0]
    assert region.points[0] == region.points[-1]
    assert [(p.x, p.y) for p in region.points] == [
        (0.0, 0.0),
        (2.0, 0.0),
        (2.0, 1.0),
        (0.0, 1.0),
        (0.0, 0.0),
    ]
    assert any(ev.kind == "gerber_region" for ev in region.provenance.evidence)
    assert {s.raw for s in region.provenance.sources} >= {"G36*", "G37*"}


def test_region_end_closes_open_linear_contour(tmp_path):
    p = _write(
        tmp_path,
        "auto_close.gbr",
        _region_file(
            "G36*\n"
            "X000000Y000000D02*\n"
            "X010000Y000000D01*\n"
            "X010000Y010000D01*\n"
            "X000000Y010000D01*\n"
            "G37*"
        ),
    )
    result = GerberRS274XParser("F.Cu").parse(p)
    assert len(result.regions) == 1
    assert result.regions[0].points[0] == result.regions[0].points[-1]
    assert len(result.regions[0].points) == 5


def test_step_repeat_expands_region_with_unique_ids_and_evidence(tmp_path):
    p = _write(
        tmp_path,
        "region_panel.gbr",
        _region_file(
            "%SRX2Y1I10.0J0.0*%\n"
            "G36*\n"
            "X000000Y000000D02*\n"
            "X010000Y000000D01*\n"
            "X010000Y010000D01*\n"
            "X000000Y010000D01*\n"
            "G37*\n"
            "%SR*%"
        ),
    )
    result = GerberRS274XParser("F.Cu").parse(p)
    assert len(result.regions) == 2
    assert len({r.id for r in result.regions}) == 2
    assert result.regions[0].points[0].x == pytest.approx(0.0)
    assert result.regions[1].points[0].x == pytest.approx(10.0)
    assert all(
        {ev.kind for ev in r.provenance.evidence}
        >= {"gerber_region", "gerber_step_repeat"}
        for r in result.regions
    )


def test_region_connects_to_overlapping_pad_as_physical_copper():
    region = CopperRegion(
        "R1",
        (
            Point(0, 0),
            Point(2, 0),
            Point(2, 2),
            Point(0, 2),
            Point(0, 0),
        ),
        "F.Cu",
    )
    pad = PadCandidate("P1", Point(1, 1), 0.5, 0.5, "C", "F.Cu")
    board = BoardModel(pads=[pad], regions=[region])

    graph = build_physical_graph(board)
    assign_physical_nets(board, graph)

    assert graph.has_edge("R1", "P1")
    assert region.net_id is not None
    assert region.net_id == pad.net_id
    assert set(board.nets[0].members) == {"R1", "P1"}


def test_region_is_indexed_and_serialized_by_board_model():
    region = CopperRegion(
        "R1",
        (Point(0, 0), Point(1, 0), Point(0, 1), Point(0, 0)),
        "F.Cu",
        provenance=Provenance(),
    )
    board = BoardModel(regions=[region])
    assert board.object_index()["R1"] is region
    assert board.to_dict()["regions"][0]["id"] == "R1"


def test_kicad_export_reports_region_omission_instead_of_silent_drop(tmp_path):
    region = CopperRegion(
        "R1",
        (Point(0, 0), Point(1, 0), Point(0, 1), Point(0, 0)),
        "F.Cu",
    )
    path, report = export_kicad_with_report(
        BoardModel(regions=[region]),
        tmp_path / "region.kicad_pcb",
    )
    assert path.exists()
    assert report.skipped_regions == 1
    assert report.skipped_region_ids == ["R1"]
    assert any(
        issue.code == "KICAD_COPPER_REGION_UNSUPPORTED"
        and issue.object_id == "R1"
        for issue in report.issues
    )


def test_multicontour_region_is_fail_closed(tmp_path):
    p = _write(
        tmp_path,
        "multicontour.gbr",
        _region_file(
            "G36*\n"
            "X000000Y000000D02*\n"
            "X010000Y000000D01*\n"
            "X020000Y020000D02*\n"
            "G37*"
        ),
    )
    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu", strict=True).parse(p)


def test_region_arc_is_fail_closed(tmp_path):
    p = _write(
        tmp_path,
        "region_arc.gbr",
        _region_file(
            "G75*\n"
            "G36*\n"
            "X010000Y000000D02*\n"
            "G03X000000Y010000I-010000J000000D01*\n"
            "G37*"
        ),
    )
    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu", strict=True).parse(p)


def test_self_intersecting_region_is_rejected(tmp_path):
    p = _write(
        tmp_path,
        "bowtie.gbr",
        _region_file(
            "G36*\n"
            "X000000Y000000D02*\n"
            "X020000Y020000D01*\n"
            "X000000Y020000D01*\n"
            "X020000Y000000D01*\n"
            "G37*"
        ),
    )
    with pytest.raises(ParseError):
        GerberRS274XParser("F.Cu", strict=True).parse(p)


def test_clear_polarity_region_is_not_claimed_supported(tmp_path):
    p = _write(
        tmp_path,
        "clear_region.gbr",
        _region_file("%LPC*%\nG36*\nM02*"),
    )
    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu", strict=True).parse(p)


def test_edge_cuts_region_is_rejected(tmp_path):
    p = _write(
        tmp_path,
        "edge_region.gbr",
        _region_file("G36*\nM02*"),
    )
    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("Edge.Cuts", strict=True).parse(p)


def test_permissive_multicontour_aborts_region_and_records_diagnostic(tmp_path):
    p = _write(
        tmp_path,
        "multicontour_permissive.gbr",
        _region_file(
            "G36*\n"
            "X000000Y000000D02*\n"
            "X010000Y000000D01*\n"
            "X020000Y020000D02*"
        ),
    )
    result = GerberRS274XParser("F.Cu", strict=False).parse(p)
    assert not result.regions
    assert any(
        d.code == "GERBER_REGION_MULTICONTOUR_UNSUPPORTED"
        for d in result.diagnostics
    )
