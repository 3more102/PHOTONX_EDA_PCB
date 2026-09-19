from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


BASE = """%FSLAX24Y24*%
%MOMM*%
"""


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(BASE + body + "M02*\n", encoding="utf-8")
    return path


def test_anisotropic_sf_scales_flash_coordinates_not_aperture(tmp_path: Path):
    path = _write(
        tmp_path,
        "sf_flash.gtl",
        "%SFA.5B3*%\n"
        "%ADD10R,2.000X1.000*%\n"
        "D10*\n"
        "X020000Y010000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    pad = result.pads[0]
    assert (pad.center.x, pad.center.y) == pytest.approx((1.0, 3.0))
    assert pad.size_x == pytest.approx(2.0)
    assert pad.size_y == pytest.approx(1.0)
    assert any(
        e.kind == "gerber_scale_factor"
        and "scale_a=0.5" in e.detail
        and "scale_b=3" in e.detail
        for e in pad.provenance.evidence
    )


def test_anisotropic_sf_scales_linear_path_not_draw_width(tmp_path: Path):
    path = _write(
        tmp_path,
        "sf_track.gtl",
        "%SFA2B0.5*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D02*\n"
        "X030000Y060000D01*\n",
    )

    track = GerberRS274XParser("F.Cu", strict=True).parse(path).tracks[0]

    assert (track.start.x, track.start.y) == pytest.approx((2.0, 1.0))
    assert (track.end.x, track.end.y) == pytest.approx((6.0, 3.0))
    assert track.width == pytest.approx(0.2)


def test_sf_does_not_scale_step_repeat_distances(tmp_path: Path):
    path = _write(
        tmp_path,
        "sf_sr.gtl",
        "%SFA2B2*%\n"
        "%ADD10C,0.300*%\n"
        "D10*\n"
        "%SRX2Y1I3.0J0*%\n"
        "X010000Y000000D03*\n"
        "%SR*%\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 2
    assert (result.pads[0].center.x, result.pads[0].center.y) == pytest.approx(
        (2.0, 0.0)
    )
    assert (result.pads[1].center.x, result.pads[1].center.y) == pytest.approx(
        (5.0, 0.0)
    )


def test_sf_composes_with_incremental_coordinates(tmp_path: Path):
    path = tmp_path / "sf_incremental.gtl"
    path.write_text(
        "%FSLIX24Y24*%\n"
        "%MOMM*%\n"
        "%SFA2B3*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y010000D02*\n"
        "X020000Y010000D01*\n"
        "M02*\n",
        encoding="utf-8",
    )

    track = GerberRS274XParser("F.Cu", strict=True).parse(path).tracks[0]

    assert (track.start.x, track.start.y) == pytest.approx((2.0, 3.0))
    assert (track.end.x, track.end.y) == pytest.approx((6.0, 6.0))


def test_mi_sf_of_ir_order_is_independent_of_command_appearance(tmp_path: Path):
    first = _write(
        tmp_path,
        "order_first.gtl",
        "%IR90*%\n"
        "%OFA3B4*%\n"
        "%SFA2B0.5*%\n"
        "%MIA1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )
    second = _write(
        tmp_path,
        "order_second.gtl",
        "%MIA1*%\n"
        "%SFA2B0.5*%\n"
        "%OFA3B4*%\n"
        "%IR90*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    a = GerberRS274XParser("F.Cu", strict=True).parse(first).pads[0]
    b = GerberRS274XParser("F.Cu", strict=True).parse(second).pads[0]

    # MI: (1,2)->(-1,2), SF: ->(-2,1), OF: ->(1,5), IR90: ->(-5,1)
    assert (a.center.x, a.center.y) == pytest.approx((-5.0, 1.0))
    assert (b.center.x, b.center.y) == pytest.approx((-5.0, 1.0))


def test_uniform_sf_supports_circular_arc_and_scales_radius(tmp_path: Path):
    path = _write(
        tmp_path,
        "sf_arc.gtl",
        "%SFA2B2*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G75*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I-010000J000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks
    assert (result.tracks[0].start.x, result.tracks[0].start.y) == pytest.approx(
        (2.0, 0.0)
    )
    assert (result.tracks[-1].end.x, result.tracks[-1].end.y) == pytest.approx(
        (0.0, 2.0)
    )
    assert all(track.width == pytest.approx(0.2) for track in result.tracks)
    assert all(
        any(
            e.kind == "gerber_arc_tessellation"
            and "radius_mm=2" in e.detail
            and "max_chord_error_mm=0.005" in e.detail
            for e in track.provenance.evidence
        )
        for track in result.tracks
    )


def test_anisotropic_sf_arc_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "sf_ellipse.gtl",
        "%SFA2B1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G75*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I-010000J000000D01*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="turns circular interpolation into non-circular geometry",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_anisotropic_sf_arc_suppresses_prior_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "sf_ellipse_permissive.gtl",
        "%SFA2B1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "G75*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I-010000J000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(
        d.code == "UNSUPPORTED_GERBER_ANISOTROPIC_ARC_SCALE"
        for d in result.diagnostics
    )


@pytest.mark.parametrize(
    "command",
    [
        "%SFA0B1*%\n",
        "%SFA0.00009B1*%\n",
        "%SFA1000B1*%\n",
        "%SFA-1B1*%\n",
        "%SFAfooB1*%\n",
    ],
)
def test_invalid_sf_fails_closed_in_strict_mode(tmp_path: Path, command: str):
    path = _write(
        tmp_path,
        "bad_sf.gtl",
        command
        + "%ADD10C,0.200*%\n"
        + "D10*\n"
        + "X000000Y000000D03*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="legacy Gerber SF",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_duplicate_sf_fails_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "duplicate_sf.gtl",
        "%SFA2B2*%\n"
        "%SFA1B1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D03*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="may only be declared once"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_late_sf_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "late_sf.gtl",
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%SFA2B2*%\n"
        "X020000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(d.code == "LATE_GERBER_SCALE_FACTOR" for d in result.diagnostics)


def test_linear_anisotropic_sf_is_preflight_ready(tmp_path: Path):
    path = _write(
        tmp_path,
        "preflight_sf.gtl",
        "%SFA2B0.5*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D02*\n"
        "X030000Y040000D01*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_anisotropic_arc_sf_is_preflight_blocker(tmp_path: Path):
    path = _write(
        tmp_path,
        "preflight_sf_arc.gtl",
        "%SFA2B1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G75*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I-010000J000000D01*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_ANISOTROPIC_ARC_SCALE" in blocker
        for blocker in report.strict_blockers
    )


def test_sf_changes_stable_object_id_on_same_source_path(tmp_path: Path):
    path = _write(
        tmp_path,
        "same_sf_source.gtl",
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )
    plain = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    path.write_text(
        BASE
        + "%SFA2B2*%\n"
        + "%ADD10C,0.200*%\n"
        + "D10*\n"
        + "X010000Y020000D03*\n"
        + "M02*\n",
        encoding="utf-8",
    )
    scaled = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    assert plain.id != scaled.id
