from pathlib import Path

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


def test_unsupported_arc_syntax_suppresses_incomplete_permissive_route(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "M15\n"
        "G03X0000Y10000R10000\n"
        "G01X0000Y20000\n"
        "M16\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.routes == []
    assert result.drills == []
    assert result.slots == []
    assert any(
        diagnostic.code == "UNSUPPORTED_EXCELLON_ROUTE_ARC_SYNTAX"
        for diagnostic in result.diagnostics
    )


def test_missing_arc_center_suppresses_incomplete_permissive_route(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "M15\n"
        "G03X0000Y10000\n"
        "G01X0000Y20000\n"
        "M16\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.routes == []
    assert any(
        diagnostic.code == "UNSUPPORTED_EXCELLON_ROUTE_ARC_CENTER"
        for diagnostic in result.diagnostics
    )


def test_invalid_arc_geometry_suppresses_incomplete_permissive_route(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "M15\n"
        "G03X0000Y20000I-10000J0000\n"
        "G01X0000Y30000\n"
        "M16\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.routes == []
    assert result.drills == []
    assert result.slots == []
    assert any(
        diagnostic.code == "EXCELLON_ROUTE_ARC_INVALID"
        for diagnostic in result.diagnostics
    )


def test_arc_before_tool_down_suppresses_following_permissive_geometry(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "G03X0000Y10000I-10000J0000\n"
        "X20000Y20000\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.routes == []
    assert result.drills == []
    assert result.slots == []
    assert any(
        diagnostic.code == "UNSUPPORTED_EXCELLON_ROUTE_SEQUENCE"
        for diagnostic in result.diagnostics
    )


def test_preflight_blocks_invalid_routed_arc_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X10000Y0000\n"
        "M15\n"
        "G03X0000Y20000I-10000J0000\n"
        "M16\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "EXCELLON_ROUTE_ARC_INVALID" in blocker
        for blocker in report.strict_blockers
    )
