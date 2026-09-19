from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


BASE = """%FSLAX24Y24*%
%MOMM*%
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "rotation.gtl"
    path.write_text(BASE + body + "M02*\n", encoding="utf-8")
    return path


def test_ir90_rotates_linear_track_counterclockwise_and_records_provenance(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%IR90*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D02*\n"
        "X030000Y020000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 1
    track = result.tracks[0]
    assert (track.start.x, track.start.y) == pytest.approx((-2.0, 1.0))
    assert (track.end.x, track.end.y) == pytest.approx((-2.0, 3.0))
    assert any(
        e.kind == "gerber_image_rotation"
        and "rotation_deg_ccw=90" in e.detail
        for e in track.provenance.evidence
    )


def test_ir270_rotates_rectangular_flash_and_swaps_dimensions(tmp_path: Path):
    path = _write(
        tmp_path,
        "%IR270*%\n"
        "%ADD10R,2.000X1.000*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    pad = result.pads[0]
    assert (pad.center.x, pad.center.y) == pytest.approx((2.0, -1.0))
    assert pad.size_x == pytest.approx(1.0)
    assert pad.size_y == pytest.approx(2.0)
    assert pad.shape == "R"


def test_ir180_rotates_outline_exactly(tmp_path: Path):
    path = _write(
        tmp_path,
        "%IR180*%\n"
        "%ADD10C,0.100*%\n"
        "D10*\n"
        "X010000Y020000D02*\n"
        "X030000Y040000D01*\n",
    )

    result = GerberRS274XParser("Edge.Cuts", strict=True).parse(path)

    assert len(result.outline) == 1
    segment = result.outline[0]
    assert (segment.start.x, segment.start.y) == pytest.approx((-1.0, -2.0))
    assert (segment.end.x, segment.end.y) == pytest.approx((-3.0, -4.0))


def test_ir90_rotates_step_repeat_offsets_after_repeat_expansion(tmp_path: Path):
    path = _write(
        tmp_path,
        "%IR90*%\n"
        "%ADD10C,0.300*%\n"
        "D10*\n"
        "%SRX2Y1I3.0J0*%\n"
        "X010000Y000000D03*\n"
        "%SR*%\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 2
    centers = [(p.center.x, p.center.y) for p in result.pads]
    assert centers == pytest.approx([(0.0, 1.0), (0.0, 4.0)])
    assert all(
        any(e.kind == "gerber_step_repeat" for e in p.provenance.evidence)
        for p in result.pads
    )
    assert all(
        any(e.kind == "gerber_image_rotation" for e in p.provenance.evidence)
        for p in result.pads
    )


def test_ir90_rotates_tessellated_arc_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%IR90*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G75*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I-010000J000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks
    assert (result.tracks[0].start.x, result.tracks[0].start.y) == pytest.approx(
        (0.0, 1.0)
    )
    assert (result.tracks[-1].end.x, result.tracks[-1].end.y) == pytest.approx(
        (-1.0, 0.0)
    )
    assert all(
        any(e.kind == "gerber_image_rotation" for e in t.provenance.evidence)
        for t in result.tracks
    )


def test_ir90_composes_with_incremental_coordinates(tmp_path: Path):
    path = tmp_path / "incremental.gtl"
    path.write_text(
        "%FSLIX24Y24*%\n"
        "%MOMM*%\n"
        "%IR90*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y000000D02*\n"
        "X000000Y020000D01*\n"
        "M02*\n",
        encoding="utf-8",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    track = result.tracks[0]
    assert (track.start.x, track.start.y) == pytest.approx((0.0, 1.0))
    assert (track.end.x, track.end.y) == pytest.approx((-2.0, 1.0))


def test_ir0_is_identity(tmp_path: Path):
    path = _write(
        tmp_path,
        "%IR0*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D02*\n"
        "X030000Y040000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    track = result.tracks[0]
    assert (track.start.x, track.start.y) == pytest.approx((1.0, 2.0))
    assert (track.end.x, track.end.y) == pytest.approx((3.0, 4.0))


@pytest.mark.parametrize("command", ["%IR45*%\n", "%IR360*%\n", "%IR-90*%\n"])
def test_invalid_ir_angle_fails_closed_in_strict_mode(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command
        + "%ADD10C,0.200*%\n"
        + "D10*\n"
        + "X000000Y000000D03*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="must be one of 0, 90, 180, or 270",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_duplicate_ir_fails_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%IR90*%\n"
        "%IR180*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D03*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="may only be declared once"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_late_ir_clears_and_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%IR90*%\n"
        "X020000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(d.code == "LATE_GERBER_IMAGE_ROTATION" for d in result.diagnostics)


def test_ir90_is_preflight_ready(tmp_path: Path):
    path = _write(
        tmp_path,
        "%IR90*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D03*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


@pytest.mark.parametrize("command", ["%SF*%\n", "%SFA1*%\n", "%SFB1*%\n", "%SFA1B1*%\n"])
def test_identity_legacy_sf_is_accepted(tmp_path: Path, command: str):
    path = _write(
        tmp_path,
        command
        + "%ADD10C,0.200*%\n"
        + "D10*\n"
        + "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    assert (result.pads[0].center.x, result.pads[0].center.y) == pytest.approx(
        (1.0, 2.0)
    )


def test_non_identity_legacy_sf_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%SFA0.5B1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert result.tracks == []
    assert any(d.code == "UNSUPPORTED_GERBER_TRANSFORM" for d in result.diagnostics)


def test_non_identity_legacy_sf_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "%SFA1B2*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="scale factor changes coordinate"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_non_identity_legacy_sf_is_preflight_blocker(tmp_path: Path):
    path = _write(
        tmp_path,
        "%SFA0.5B1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_TRANSFORM" in blocker
        for blocker in report.strict_blockers
    )


def test_malformed_legacy_sf_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%SFAfooB1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert result.tracks == []
    assert any(d.code == "INVALID_GERBER_SCALE_FACTOR" for d in result.diagnostics)
