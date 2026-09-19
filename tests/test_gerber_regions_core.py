from pathlib import Path

import pytest

from photonx_eda_pcb.connectivity import build_physical_graph, assign_physical_nets
from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.models import BoardModel, CopperRegion, PadCandidate, Point
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight
from photonx_eda_pcb.provenance import Provenance


def _write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _region_file(body: str, *, fs: str = "%FSLAX24Y24*%") -> str:
    return fs + "\n%MOMM*%\n" + body + "\nM02*\n"


def test_linear_dark_region_is_reconstructed_with_provenance(tmp_path: Path):
    path = _write(
        tmp_path,
        "region.gtl",
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

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert not result.tracks
    assert not result.pads
    assert len(result.regions) == 1
    region = result.regions[0]
    assert [(point.x, point.y) for point in region.points] == [
        (0.0, 0.0),
        (2.0, 0.0),
        (2.0, 1.0),
        (0.0, 1.0),
        (0.0, 0.0),
    ]
    assert any(event.kind == "gerber_region" for event in region.provenance.evidence)
    assert {source.raw for source in region.provenance.sources} >= {"G36*", "G37*"}


def test_region_end_does_not_implicitly_close_open_contour(tmp_path: Path):
    path = _write(
        tmp_path,
        "open_contour.gtl",
        _region_file(
            "G36*\n"
            "X000000Y000000D02*\n"
            "X010000Y000000D01*\n"
            "X010000Y010000D01*\n"
            "X000000Y010000D01*\n"
            "G37*"
        ),
    )

    with pytest.raises(ParseError, match="does not implicitly close"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_step_repeat_expands_region_with_unique_ids_and_evidence(tmp_path: Path):
    path = _write(
        tmp_path,
        "region_panel.gtl",
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

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 2
    assert len({region.id for region in result.regions}) == 2
    assert result.regions[0].points[0].x == pytest.approx(0.0)
    assert result.regions[1].points[0].x == pytest.approx(10.0)
    assert all(
        {event.kind for event in region.provenance.evidence}
        >= {"gerber_region", "gerber_step_repeat"}
        for region in result.regions
    )


def test_g75_semicircle_region_is_reconstructed_with_bounded_tessellation(tmp_path: Path):
    path = _write(
        tmp_path,
        "g75_semicircle.gtl",
        _region_file(
            "G75*\n"
            "G36*\n"
            "X000000Y000000D02*\n"
            "X020000Y000000D01*\n"
            "G03*\n"
            "X000000Y000000I-010000J000000D01*\n"
            "G37*"
        ),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    region = result.regions[0]
    assert region.points[0] == region.points[-1]
    assert len(region.points) > 8
    evidence = {event.kind for event in region.provenance.evidence}
    assert "gerber_region_arc_tessellation" in evidence
    assert "gerber_region" in evidence

    from photonx_eda_pcb.geometry_kernel import region_shape

    assert region_shape(region).area == pytest.approx(1.57079632679, abs=0.01)


def test_g75_full_circle_can_form_entire_region_contour(tmp_path: Path):
    path = _write(
        tmp_path,
        "g75_full_circle.gtl",
        _region_file(
            "G75*\n"
            "G36*\n"
            "X010000Y000000D02*\n"
            "G03*\n"
            "X010000Y000000I-010000J000000D01*\n"
            "G37*"
        ),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    from photonx_eda_pcb.geometry_kernel import region_shape

    assert region_shape(result.regions[0]).area == pytest.approx(3.14159265359, abs=0.02)


def test_g75_region_arc_supports_incremental_endpoints(tmp_path: Path):
    path = _write(
        tmp_path,
        "g75_incremental_arc.gtl",
        _region_file(
            "G75*\n"
            "G36*\n"
            "X000000Y000000D02*\n"
            "X020000Y000000D01*\n"
            "G03*\n"
            "X-020000Y000000I-010000J000000D01*\n"
            "G37*",
            fs="%FSLIX24Y24*%",
        ),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    assert result.regions[0].points[0] == result.regions[0].points[-1]


def test_g75_region_arc_tessellation_bounds_anisotropic_image_scaling(tmp_path: Path):
    path = _write(
        tmp_path,
        "g75_scaled_arc.gtl",
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%SFA2B3*%\n"
        "G75*\n"
        "G36*\n"
        "X000000Y000000D02*\n"
        "X020000Y000000D01*\n"
        "G03*\n"
        "X000000Y000000I-010000J000000D01*\n"
        "G37*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    region = result.regions[0]
    xs = [point.x for point in region.points]
    ys = [point.y for point in region.points]
    assert min(xs) == pytest.approx(0.0)
    assert max(xs) == pytest.approx(4.0)
    assert min(ys) == pytest.approx(0.0)
    assert max(ys) == pytest.approx(3.0, abs=0.01)


def test_g75_inside_active_region_is_rejected_by_region_grammar(tmp_path: Path):
    path = _write(
        tmp_path,
        "late_g75.gtl",
        _region_file(
            "G36*\n"
            "X000000Y000000D02*\n"
            "G75*\n"
            "G37*"
        ),
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="only D01/D02 and G01/G02/G03",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_incremental_modal_region_coordinates_are_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "incremental_region.gtl",
        _region_file(
            "G36*\n"
            "D02*\n"
            "X010000Y010000*\n"
            "D01*\n"
            "X010000Y000000*\n"
            "X000000Y010000*\n"
            "X-010000Y000000*\n"
            "X000000Y-010000*\n"
            "G37*",
            fs="%FSLIX24Y24*%",
        ),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    assert [(point.x, point.y) for point in result.regions[0].points] == [
        (1.0, 1.0),
        (2.0, 1.0),
        (2.0, 2.0),
        (1.0, 2.0),
        (1.0, 1.0),
    ]


def test_image_transforms_apply_exactly_to_region_vertices(tmp_path: Path):
    path = _write(
        tmp_path,
        "transformed_region.gtl",
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%MIA1*%\n"
        "%SFA2B0.5*%\n"
        "%OFA1B-2*%\n"
        "%IR90*%\n"
        "G36*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "X010000Y020000D01*\n"
        "X000000Y020000D01*\n"
        "X000000Y000000D01*\n"
        "G37*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    actual = [(point.x, point.y) for point in result.regions[0].points]
    expected = [(2.0, 1.0), (2.0, -1.0), (1.0, -1.0), (1.0, 1.0), (2.0, 1.0)]
    for got, want in zip(actual, expected):
        assert got[0] == pytest.approx(want[0])
        assert got[1] == pytest.approx(want[1])
    evidence = {event.kind for event in result.regions[0].provenance.evidence}
    assert {"gerber_region", "gerber_mirror_image", "gerber_scale_factor", "gerber_image_offset", "gerber_image_rotation"} <= evidence


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


def test_kicad_export_reports_region_omission_instead_of_silent_drop(tmp_path: Path):
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


def test_multicontour_region_is_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "multicontour.gtl",
        _region_file(
            "G36*\n"
            "X000000Y000000D02*\n"
            "X010000Y000000D01*\n"
            "X020000Y020000D02*\n"
            "G37*"
        ),
    )

    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_g74_region_arc_remains_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "region_g74_arc.gtl",
        _region_file(
            "G74*\n"
            "G36*\n"
            "X020000Y000000D02*\n"
            "G03X000000Y000000I010000J000000D01*\n"
            "G37*"
        ),
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="require G75 multi-quadrant mode",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_self_intersecting_region_is_rejected(tmp_path: Path):
    path = _write(
        tmp_path,
        "bowtie.gtl",
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
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_edge_cuts_region_is_rejected(tmp_path: Path):
    path = _write(
        tmp_path,
        "edge_region.gko",
        _region_file("G36*\nM02*"),
    )

    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("Edge.Cuts", strict=True).parse(path)


def test_permissive_multicontour_aborts_region_and_records_diagnostic(tmp_path: Path):
    path = _write(
        tmp_path,
        "multicontour_permissive.gtl",
        _region_file(
            "G36*\n"
            "X000000Y000000D02*\n"
            "X010000Y000000D01*\n"
            "X020000Y020000D02*"
        ),
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert not result.regions
    assert any(
        diagnostic.code == "GERBER_REGION_MULTICONTOUR_UNSUPPORTED"
        for diagnostic in result.diagnostics
    )


def test_unterminated_region_is_a_preflight_blocker(tmp_path: Path):
    path = _write(
        tmp_path,
        "unterminated.gtl",
        "%FSLAX24Y24*%\n%MOMM*%\nG36*\nM02*\n",
    )

    report = preflight(path)

    assert not report.ready_for_strict_reconstruction
    assert any("GERBER_REGION_UNTERMINATED" in blocker for blocker in report.strict_blockers)
