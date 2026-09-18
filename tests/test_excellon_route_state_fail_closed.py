from pathlib import Path

import pytest

from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.preflight import preflight


HEADER = """M48
METRIC
T01C1.000
T02C0.800
%
T01
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "route_state.drl"
    path.write_text(HEADER + body + "M30\n", encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("body", "expected_code"),
    [
        (
            "X1000Y1000\n"
            "G00X0000Y0000\n"
            "M15\n"
            "G01XBADY1000\n"
            "M16\n",
            "MALFORMED_EXCELLON_ROUTE",
        ),
        (
            "X1000Y1000\n"
            "G85X0000Y0000X1000\n",
            "UNSUPPORTED_EXCELLON_SLOT",
        ),
        (
            "X1000Y1000\n"
            "G00X0000Y0000\n"
            "M15\n"
            "T02\n"
            "M16\n",
            "EXCELLON_ROUTE_STATE",
        ),
        (
            "X1000Y1000\n"
            "G00X0000Y0000\n"
            "M15\n"
            "X2000Y2000\n"
            "M16\n",
            "EXCELLON_ROUTE_STATE",
        ),
        (
            "X1000Y1000\n"
            "G00X0000Y0000\n"
            "M15\n"
            "G05\n"
            "M16\n",
            "EXCELLON_ROUTE_STATE",
        ),
    ],
)
def test_route_or_slot_state_violation_clears_prior_permissive_geometry(
    tmp_path: Path,
    body: str,
    expected_code: str,
):
    path = _write(tmp_path, body)

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []
    assert any(diagnostic.code == expected_code for diagnostic in result.diagnostics)


def test_empty_route_end_suppresses_permissive_file_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "X1000Y1000\n"
        "G00X0000Y0000\n"
        "M15\n"
        "M16\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []
    assert any(
        diagnostic.code == "EXCELLON_ROUTE_EMPTY"
        for diagnostic in result.diagnostics
    )


def test_unterminated_route_suppresses_permissive_file_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "X1000Y1000\n"
        "G00X0000Y0000\n"
        "M15\n"
        "G01X1000Y0000\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []
    assert any(
        diagnostic.code == "EXCELLON_ROUTE_UNTERMINATED"
        for diagnostic in result.diagnostics
    )


def test_valid_linear_route_remains_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X0000Y0000\n"
        "M15\n"
        "G01X1000Y0000\n"
        "M16\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.routes) == 1
    assert result.routes[0].points[0] == pytest.approx((0.0, 0.0))
    assert result.routes[0].points[-1] == pytest.approx((1.0, 0.0))


def test_preflight_blocks_route_state_violation(tmp_path: Path):
    path = _write(
        tmp_path,
        "G00X0000Y0000\n"
        "M15\n"
        "T02\n"
        "M16\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "EXCELLON_ROUTE_STATE" in blocker
        for blocker in report.strict_blockers
    )
