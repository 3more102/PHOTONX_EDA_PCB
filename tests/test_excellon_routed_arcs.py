from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.excellon_routing.arc_commands import (
    parse_arc_route_command,
    parse_radius_arc_route_command,
)
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
    )


def test_parse_standard_xnc_radius_arc_command():
    assert parse_radius_arc_route_command("G03X0000Y10000A10000") == (
        "G03",
        "0000",
        "10000",
        "10000",
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
    midpoint = route.points[len(route.points) // 2]
    assert midpoint[0] > 5.0
    assert midpoint[1] > 5.0
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


def test_standard_xnc_radius_form_arc_is_supported(tmp_path: Path):
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
    assert route.points[0] == pytest.approx((10.0, 0.0))
    assert route.points[-1] == pytest.approx((0.0, 10.0))
    midpoint = route.points[len(route.points) // 2]
    assert midpoint[0] > 5.0
    assert midpoint[1] > 5.0
    assert any(
        evidence.kind == "excellon_route_arc_tessellation"
        and "encoding=radius" in evidence.detail
        for evidence in route.provenance.evidence
    )


def test_standard_xnc_decimal_radius_example_is_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X5.05Y2.6\n"
        "M15\n"
        "G03X6.0Y1.6A1.0\n"
        "M16\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.routes) == 1
    route = result.routes[0]
    assert route.points[0] == pytest.approx((5.05, 2.6))
    assert route.points[-1] == pytest.approx((6.0, 1.6))
    assert any(
        evidence.kind == "excellon_route_arc_tessellation"
        and "encoding=radius" in evidence.detail
        for evidence in route.provenance.evidence
    )


def test_standard_xnc_radius_form_cw_selects_other_center(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "M15\n"
        "G02X0000Y10000A10000\n"
        "M16\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    route = result.routes[0]
    assert route.points[-1] == pytest.approx((0.0, 10.0))
    midpoint = route.points[len(route.points) // 2]
    assert midpoint[0] < 5.0
    assert midpoint[1] < 5.0
    assert any(
        evidence.kind == "excellon_route_arc_tessellation"
        and "encoding=radius" in evidence.detail
        for evidence in route.provenance.evidence
    )


def test_standard_xnc_radius_form_allows_180_degree_semicircle(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X0000Y0000\n"
        "M15\n"
        "G03X10000Y0000A5000\n"
        "M16\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.routes) == 1
    route = result.routes[0]
    assert route.points[0] == pytest.approx((0.0, 0.0))
    assert route.points[-1] == pytest.approx((10.0, 0.0))
    assert len(route.points) > 2
    assert any(abs(point[1]) > 0.1 for point in route.points[1:-1])


def test_radius_form_arc_rejects_radius_smaller_than_half_chord(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X0000Y0000\n"
        "M15\n"
        "G03X10000Y0000A4000\n"
        "M16\n",
    )

    with pytest.raises(ParseError, match="exceeds diameter"):
        ExcellonParser(strict=True).parse(path)


def test_radius_form_arc_rejects_coincident_endpoints(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "M15\n"
        "G03X10000Y0000A10000\n"
        "M16\n",
    )

    with pytest.raises(ParseError, match="coincide"):
        ExcellonParser(strict=True).parse(path)


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


def test_preflight_accepts_standard_xnc_radius_arc(tmp_path: Path):
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
