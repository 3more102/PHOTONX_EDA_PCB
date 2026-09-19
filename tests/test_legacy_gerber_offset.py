from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


BASE = """%FSLAX24Y24*%
%MOMM*%
"""


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(BASE + body + "M02*\n", encoding="utf-8")
    return path


def test_of_translates_linear_geometry_in_active_units(tmp_path: Path):
    path = _write(
        tmp_path,
        "offset_track.gtl",
        "%OFA1.5B-2.0*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D02*\n"
        "X030000Y040000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    track = result.tracks[0]
    assert (track.start.x, track.start.y) == pytest.approx((2.5, 0.0))
    assert (track.end.x, track.end.y) == pytest.approx((4.5, 2.0))
    assert any(
        e.kind == "gerber_image_offset"
        and "offset_mm=(1.5,-2)" in e.detail
        for e in track.provenance.evidence
    )


def test_of_translates_flash_without_changing_aperture_size(tmp_path: Path):
    path = _write(
        tmp_path,
        "offset_flash.gtl",
        "%OFA-1B3*%\n"
        "%ADD10R,2.000X1.000*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    pad = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    assert (pad.center.x, pad.center.y) == pytest.approx((0.0, 5.0))
    assert pad.size_x == pytest.approx(2.0)
    assert pad.size_y == pytest.approx(1.0)


def test_of_respects_inch_units(tmp_path: Path):
    path = tmp_path / "offset_inch.gtl"
    path.write_text(
        "%FSLAX24Y24*%\n"
        "%MOIN*%\n"
        "%OFA0.100B-0.050*%\n"
        "%ADD10C,0.010*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
        encoding="utf-8",
    )

    pad = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    assert (pad.center.x, pad.center.y) == pytest.approx((2.54, -1.27))


@pytest.mark.parametrize(
    "command",
    ["%OF*%\n", "%OFA0*%\n", "%OFB0*%\n", "%OFA0B0*%\n"],
)
def test_identity_of_forms_are_accepted(tmp_path: Path, command: str):
    path = _write(
        tmp_path,
        "identity_of.gtl",
        command
        + "%ADD10C,0.200*%\n"
        + "D10*\n"
        + "X010000Y020000D03*\n",
    )

    pad = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]
    assert (pad.center.x, pad.center.y) == pytest.approx((1.0, 2.0))


def test_of_translates_all_step_repeat_instances_equally(tmp_path: Path):
    path = _write(
        tmp_path,
        "offset_sr.gtl",
        "%OFA10B20*%\n"
        "%ADD10C,0.300*%\n"
        "D10*\n"
        "%SRX2Y1I3.0J0*%\n"
        "X010000Y000000D03*\n"
        "%SR*%\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 2
    assert (result.pads[0].center.x, result.pads[0].center.y) == pytest.approx(
        (11.0, 20.0)
    )
    assert (result.pads[1].center.x, result.pads[1].center.y) == pytest.approx(
        (14.0, 20.0)
    )


def test_mi_of_ir_order_is_independent_of_command_appearance(tmp_path: Path):
    a = _write(
        tmp_path,
        "order_a.gtl",
        "%IR90*%\n"
        "%OFA3B4*%\n"
        "%MIA1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )
    b = _write(
        tmp_path,
        "order_b.gtl",
        "%MIA1*%\n"
        "%OFA3B4*%\n"
        "%IR90*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    pa = GerberRS274XParser("F.Cu", strict=True).parse(a).pads[0]
    pb = GerberRS274XParser("F.Cu", strict=True).parse(b).pads[0]

    # MI: (1,2)->(-1,2), OF: ->(2,6), IR90: ->(-6,2)
    assert (pa.center.x, pa.center.y) == pytest.approx((-6.0, 2.0))
    assert (pb.center.x, pb.center.y) == pytest.approx((-6.0, 2.0))


def test_of_translates_tessellated_arc_before_ir(tmp_path: Path):
    path = _write(
        tmp_path,
        "offset_arc.gtl",
        "%OFA2B3*%\n"
        "%IR90*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G75*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I-010000J000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks
    # Source start (1,0) + OF -> (3,3), then IR90 -> (-3,3)
    assert (result.tracks[0].start.x, result.tracks[0].start.y) == pytest.approx(
        (-3.0, 3.0)
    )
    # Source end (0,1) + OF -> (2,4), then IR90 -> (-4,2)
    assert (
        result.tracks[-1].end.x,
        result.tracks[-1].end.y,
    ) == pytest.approx((-4.0, 2.0))


@pytest.mark.parametrize(
    "command",
    [
        "%OFA100000B0*%\n",
        "%OFA0B-100000*%\n",
        "%OFA1.123456B0*%\n",
        "%OFAX1B0*%\n",
    ],
)
def test_invalid_of_fails_closed_in_strict_mode(tmp_path: Path, command: str):
    path = _write(
        tmp_path,
        "bad_of.gtl",
        command
        + "%ADD10C,0.200*%\n"
        + "D10*\n"
        + "X000000Y000000D03*\n",
    )

    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_of_requires_explicit_units(tmp_path: Path):
    path = tmp_path / "offset_no_units.gtl"
    path.write_text(
        "%FSLAX24Y24*%\n"
        "%OFA1B2*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
        encoding="utf-8",
    )

    with pytest.raises(ParseError, match="before explicit MO/G70/G71"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_duplicate_of_fails_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "duplicate_of.gtl",
        "%OFA1B0*%\n"
        "%OFA2B0*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D03*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="may only be declared once"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_late_of_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "late_of.gtl",
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%OFA1B0*%\n"
        "X020000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(d.code == "LATE_GERBER_OFFSET" for d in result.diagnostics)


def test_of_is_preflight_ready(tmp_path: Path):
    path = _write(
        tmp_path,
        "preflight_of.gtl",
        "%OFA1B-2*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_of_changes_stable_object_id_on_same_source_path(tmp_path: Path):
    path = _write(
        tmp_path,
        "same_of_source.gtl",
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )
    plain = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    path.write_text(
        BASE
        + "%OFA1B0*%\n"
        + "%ADD10C,0.200*%\n"
        + "D10*\n"
        + "X010000Y020000D03*\n"
        + "M02*\n",
        encoding="utf-8",
    )
    shifted = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    assert plain.id != shifted.id
