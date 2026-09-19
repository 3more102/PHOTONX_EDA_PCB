from pathlib import Path

import pytest

from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


BASE = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,0.200*%
D10*
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(BASE + body + "M02*\n", encoding="utf-8")
    return path


@pytest.mark.parametrize("command", ["G91*", "G091*"])
def test_incremental_coordinate_mode_accumulates_xy_deltas(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X010000Y020000D02*\n"
        "X010000D01*\n"
        "Y-010000D01*\n"
        "X-005000Y005000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 2
    assert result.tracks[0].start == pytest.approx((1.0, 2.0))
    assert result.tracks[0].end == pytest.approx((2.0, 2.0))
    assert result.tracks[1].start == pytest.approx((2.0, 2.0))
    assert result.tracks[1].end == pytest.approx((2.0, 1.0))
    assert len(result.pads) == 1
    assert (result.pads[0].center.x, result.pads[0].center.y) == pytest.approx(
        (1.5, 1.5)
    )


@pytest.mark.parametrize(
    ("incremental_command", "absolute_command"),
    [("G91*", "G90*"), ("G091*", "G090*")],
)
def test_legacy_coordinate_mode_switching_is_modal(
    tmp_path: Path,
    incremental_command: str,
    absolute_command: str,
):
    path = _write(
        tmp_path,
        incremental_command + "\n"
        "X010000Y010000D02*\n"
        + absolute_command
        + "\n"
        "X030000Y040000D02*\n"
        + incremental_command
        + "\n"
        "X010000Y-010000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    assert (result.pads[0].center.x, result.pads[0].center.y) == pytest.approx(
        (4.0, 3.0)
    )


def test_incremental_arc_accumulates_endpoint_and_keeps_ij_as_center_offsets(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "G91*\n"
        "G75*\n"
        "X010000Y000000D02*\n"
        "G03X-010000Y010000I-010000J000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks
    assert result.tracks[0].start == pytest.approx((1.0, 0.0))
    assert result.tracks[-1].end == pytest.approx((0.0, 1.0))
    assert any(
        evidence.kind == "gerber_arc_tessellation"
        for track in result.tracks
        for evidence in track.provenance.evidence
    )


def test_explicit_absolute_mode_remains_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "G90*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 1
    assert result.tracks[0].start == pytest.approx((0.0, 0.0))
    assert result.tracks[0].end == pytest.approx((1.0, 0.0))


@pytest.mark.parametrize("command", ["G91*", "G091*"])
def test_preflight_accepts_supported_incremental_coordinate_mode(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X010000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not any(
        "GERBER_INCREMENTAL_COORDINATES_UNSUPPORTED" in blocker
        for blocker in report.strict_blockers
    )
