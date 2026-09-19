from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.preflight import preflight


HEADER = """M48
METRIC
T01C0.600
%
T01
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "top.drl"
    path.write_text(HEADER + body + "M30\n", encoding="utf-8")
    return path


@pytest.mark.parametrize("command", ["ICI,ON", "G91"])
def test_incremental_excellon_drill_hits_accumulate_from_previous_coordinate(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X1.000Y1.000\n"
        "X1.000Y0.000\n"
        "Y0.500\n"
        "X-0.250\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.drills) == 4
    assert (result.drills[0].center.x, result.drills[0].center.y) == pytest.approx((1.0, 1.0))
    assert (result.drills[1].center.x, result.drills[1].center.y) == pytest.approx((2.0, 1.0))
    assert (result.drills[2].center.x, result.drills[2].center.y) == pytest.approx((2.0, 1.5))
    assert (result.drills[3].center.x, result.drills[3].center.y) == pytest.approx((1.75, 1.5))
    assert result.diagnostics == []


@pytest.mark.parametrize(
    ("incremental_command", "absolute_command"),
    [("ICI,ON", "ICI,OFF"), ("G91", "G90")],
)
def test_excellon_coordinate_mode_switching_is_modal(
    tmp_path: Path,
    incremental_command: str,
    absolute_command: str,
):
    path = _write(
        tmp_path,
        incremental_command + "\n"
        "X1.000Y1.000\n"
        "X1.000Y0.000\n"
        + absolute_command
        + "\n"
        "X3.000Y4.000\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert [(d.center.x, d.center.y) for d in result.drills] == pytest.approx(
        [(1.0, 1.0), (2.0, 1.0), (3.0, 4.0)]
    )


@pytest.mark.parametrize("command", ["ICI,ON", "G91"])
def test_incremental_excellon_linear_route_endpoints_accumulate(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "G00X1.000Y1.000\n"
        "M15\n"
        "G01X1.000Y0.000\n"
        "G01Y1.000\n"
        "M16\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.routes) == 1
    assert result.routes[0].points == pytest.approx(
        ((1.0, 1.0), (2.0, 1.0), (2.0, 2.0))
    )


@pytest.mark.parametrize("command", ["ICI,ON", "G91"])
def test_incremental_excellon_routed_arc_accumulates_endpoint_but_keeps_ij_as_offsets(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "G00X1.000Y1.000\n"
        "M15\n"
        "G02X1.000Y0.000I0.500J0.000\n"
        "M16\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.routes) == 1
    assert result.routes[0].points[0] == pytest.approx((1.0, 1.0))
    assert result.routes[0].points[-1] == pytest.approx((2.0, 1.0))
    assert any(
        evidence.kind == "excellon_route_arc_tessellation"
        for evidence in result.routes[0].provenance.evidence
    )


@pytest.mark.parametrize("command", ["ICI,ON", "G91"])
def test_incremental_g85_slots_remain_fail_closed_until_canned_slot_semantics_are_modeled(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X1.000Y1.000G85X1.000Y0.000\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="incremental Excellon G85 slot coordinates are not yet modeled",
    ):
        ExcellonParser(strict=True).parse(path)

    result = ExcellonParser(strict=False).parse(path)
    assert result.drills == []
    assert result.slots == []
    assert result.routes == []
    assert any(
        diagnostic.code == "UNSUPPORTED_EXCELLON_INCREMENTAL_SLOT"
        for diagnostic in result.diagnostics
    )


@pytest.mark.parametrize("command", ["ICI,ON", "G91"])
def test_preflight_accepts_supported_incremental_excellon_drill_files(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X1.000Y1.000\n"
        "X1.000Y0.000\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not any(
        "UNSUPPORTED_EXCELLON_INCREMENTAL" in blocker
        for blocker in report.strict_blockers
    )


@pytest.mark.parametrize("command", ["ICI,OFF", "G90"])
def test_explicit_absolute_excellon_modes_remain_supported(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X1.000Y1.000\n"
        "X2.000Y1.000\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.drills) == 2
    assert result.drills[0].center.x == pytest.approx(1.0)
    assert result.drills[1].center.x == pytest.approx(2.0)
