from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.excellon_routing.arc_commands import parse_arc_route_command
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.preflight import preflight


HEADER = """M48
METRIC
T01C1.000
%
T01
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "route.drl"
    path.write_text(HEADER + body + "M30\n", encoding="utf-8")
    return path


def test_parse_supported_excellon_arc_command():
    assert parse_arc_route_command("G03X0000Y10000I-10000J0000") == (
        "G03",
        "0000",
        "10000",
        "-10000",
        "0000",
        None,
    )


def test_ccw_routed_arc_is_tessellated_into_route_points(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "M15\n"
        "G03X0000Y10000I-10000J0000\n"
        "M16\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.routes) == 1
    route = result.routes[0]
    assert len(route.points) > 2
    assert route.points[0] == pytest.approx((10.0, 0.0))
    assert route.points[-1] == pytest.approx((0.0, 10.0))
    assert any(
        evidence.kind == "excellon_route_arc_tessellation"
        for evidence in route.provenance.evidence
    )


def test_cw_routed_arc_is_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X0000Y10000\n"
        "M15\n"
        "G02X10000Y0000I0000J-10000\n"
        "M16\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.routes) == 1
    assert result.routes[0].points[-1] == pytest.approx((10.0, 0.0))


def test_route_can_mix_linear_and_arc_segments(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X0000Y0000\n"
        "M15\n"
        "G01X10000Y0000\n"
        "G03X0000Y10000I-10000J0000\n"
        "G01X0000Y20000\n"
        "M16\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    route = result.routes[0]
    assert route.points[0] == pytest.approx((0.0, 0.0))
    assert route.points[-1] == pytest.approx((0.0, 20.0))
    assert len(route.points) > 4


def test_routed_arc_requires_tool_down(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "G03X0000Y10000I-10000J0000\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="requires G00/M15"):
        ExcellonParser(strict=True).parse(path)


def test_parse_supported_excellon_radius_arc_command():
    assert parse_arc_route_command("G03X0000Y10000A10000") == (
        "G03",
        "0000",
        "10000",
        None,
        None,
        "10000",
    )


def test_radius_form_arc_is_tessellated_with_radius_evidence(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "M15\n"
        "G03X0000Y10000A10000\n"
        "M16\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.routes) == 1
    route = result.routes[0]
    assert len(route.points) > 2
    assert route.points[0] == pytest.approx((10.0, 0.0))
    assert route.points[-1] == pytest.approx((0.0, 10.0))
    evidence = [
        item
        for item in route.provenance.evidence
        if item.kind == "excellon_route_arc_tessellation"
    ]
    assert evidence
    assert "definition=radius" in evidence[0].detail
    assert "requested_radius_mm=10" in evidence[0].detail


def test_radius_form_arc_rejects_radius_smaller_than_half_chord(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X0000Y0000\n"
        "M15\n"
        "G03X20000Y0000A5000\n"
        "M16\n",
    )

    with pytest.raises(ParseError, match="too small for chord"):
        ExcellonParser(strict=True).parse(path)


def test_radius_form_arc_rejects_mixed_radius_and_center_offsets(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "M15\n"
        "G03X0000Y10000I-10000J0000A10000\n"
        "M16\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="cannot mix A# radius"):
        ExcellonParser(strict=True).parse(path)


def test_radius_form_arc_requires_inline_endpoint(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "M15\n"
        "G03A10000\n"
        "M16\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert any(
        d.code == "UNSUPPORTED_EXCELLON_ROUTE_ARC_RADIUS"
        for d in result.diagnostics
    )


def test_preflight_accepts_supported_excellon_radius_arc(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "M15\n"
        "G03X0000Y10000A10000\n"
        "M16\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction


def test_invalid_routed_arc_geometry_is_not_silently_accepted(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "M15\n"
        "G03X0000Y20000I-10000J0000\n"
        "M16\n",
    )

    with pytest.raises(ParseError, match="invalid Excellon routed arc"):
        ExcellonParser(strict=True).parse(path)


def test_preflight_accepts_supported_excellon_routed_arc(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "M15\n"
        "G03X0000Y10000I-10000J0000\n"
        "M16\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
