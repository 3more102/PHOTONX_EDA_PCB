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


def test_mia1_mirrors_x_coordinate_only(tmp_path: Path):
    path = _write(
        tmp_path,
        "mirror_a.gtl",
        "%MIA1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D02*\n"
        "X030000Y040000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 1
    track = result.tracks[0]
    assert (track.start.x, track.start.y) == pytest.approx((-1.0, 2.0))
    assert (track.end.x, track.end.y) == pytest.approx((-3.0, 4.0))
    assert any(
        e.kind == "gerber_mirror_image"
        and "mirror_a=1" in e.detail
        and "mirror_b=0" in e.detail
        for e in track.provenance.evidence
    )


def test_mib1_mirrors_y_coordinate_only(tmp_path: Path):
    path = _write(
        tmp_path,
        "mirror_b.gtl",
        "%MIB1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D02*\n"
        "X030000Y040000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    track = result.tracks[0]
    assert (track.start.x, track.start.y) == pytest.approx((1.0, -2.0))
    assert (track.end.x, track.end.y) == pytest.approx((3.0, -4.0))


def test_mia1b1_mirrors_both_coordinate_axes(tmp_path: Path):
    path = _write(
        tmp_path,
        "mirror_both.gtl",
        "%MIA1B1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    pad = result.pads[0]
    assert (pad.center.x, pad.center.y) == pytest.approx((-1.0, -2.0))


@pytest.mark.parametrize("command", ["%MI*%\n", "%MIA0*%\n", "%MIB0*%\n", "%MIA0B0*%\n"])
def test_identity_mi_forms_are_accepted(tmp_path: Path, command: str):
    path = _write(
        tmp_path,
        "identity_mi.gtl",
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


def test_mi_does_not_mirror_aperture_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "mirror_aperture.gtl",
        "%MIA1*%\n"
        "%ADD10R,2.000X1.000*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    pad = result.pads[0]
    assert (pad.center.x, pad.center.y) == pytest.approx((-1.0, 2.0))
    assert pad.size_x == pytest.approx(2.0)
    assert pad.size_y == pytest.approx(1.0)


def test_mi_does_not_mirror_step_repeat_distances(tmp_path: Path):
    path = _write(
        tmp_path,
        "mirror_sr.gtl",
        "%MIA1*%\n"
        "%ADD10C,0.300*%\n"
        "D10*\n"
        "%SRX2Y1I3.0J0*%\n"
        "X010000Y000000D03*\n"
        "%SR*%\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 2
    assert (result.pads[0].center.x, result.pads[0].center.y) == pytest.approx(
        (-1.0, 0.0)
    )
    assert (result.pads[1].center.x, result.pads[1].center.y) == pytest.approx(
        (2.0, 0.0)
    )
    assert all(
        any(e.kind == "gerber_step_repeat" for e in p.provenance.evidence)
        for p in result.pads
    )


def test_mi_then_ir_order_is_independent_of_command_appearance(tmp_path: Path):
    first_ir = _write(
        tmp_path,
        "ir_then_mi.gtl",
        "%IR90*%\n"
        "%MIA1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )
    first_mi = _write(
        tmp_path,
        "mi_then_ir.gtl",
        "%MIA1*%\n"
        "%IR90*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    a = GerberRS274XParser("F.Cu", strict=True).parse(first_ir).pads[0]
    b = GerberRS274XParser("F.Cu", strict=True).parse(first_mi).pads[0]

    assert (a.center.x, a.center.y) == pytest.approx((-2.0, -1.0))
    assert (b.center.x, b.center.y) == pytest.approx((-2.0, -1.0))


def test_mi_composes_with_incremental_coordinates(tmp_path: Path):
    path = tmp_path / "mirror_incremental.gtl"
    path.write_text(
        "%FSLIX24Y24*%\n"
        "%MOMM*%\n"
        "%MIB1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y010000D02*\n"
        "X020000Y030000D01*\n"
        "M02*\n",
        encoding="utf-8",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    track = result.tracks[0]
    assert (track.start.x, track.start.y) == pytest.approx((1.0, -1.0))
    assert (track.end.x, track.end.y) == pytest.approx((3.0, -4.0))


def test_mi_transforms_tessellated_arc_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "mirror_arc.gtl",
        "%MIA1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G75*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I-010000J000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks
    assert (result.tracks[0].start.x, result.tracks[0].start.y) == pytest.approx(
        (-1.0, 0.0)
    )
    assert (result.tracks[-1].end.x, result.tracks[-1].end.y) == pytest.approx(
        (0.0, 1.0)
    )
    assert all(
        any(e.kind == "gerber_mirror_image" for e in t.provenance.evidence)
        for t in result.tracks
    )


@pytest.mark.parametrize(
    "command",
    ["%MIA2*%\n", "%MIB-1*%\n", "%MIA1B2*%\n", "%MIX1*%\n"],
)
def test_invalid_mi_fails_closed_in_strict_mode(tmp_path: Path, command: str):
    path = _write(
        tmp_path,
        "bad_mi.gtl",
        command
        + "%ADD10C,0.200*%\n"
        + "D10*\n"
        + "X000000Y000000D03*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="optional A0/A1 and B0/B1"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_duplicate_mi_fails_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "duplicate_mi.gtl",
        "%MIA1*%\n"
        "%MIB1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D03*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="may only be declared once"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_late_mi_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "late_mi.gtl",
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%MIA1*%\n"
        "X020000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(d.code == "LATE_GERBER_MIRROR_IMAGE" for d in result.diagnostics)


def test_mi_is_preflight_ready(tmp_path: Path):
    path = _write(
        tmp_path,
        "preflight_mi.gtl",
        "%MIA1B1*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_transform_changes_stable_object_id(tmp_path: Path):
    path = _write(
        tmp_path,
        "same_source.gtl",
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X010000Y020000D03*\n",
    )
    plain_pad = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    path.write_text(
        BASE
        + "%MIA1*%\n"
        + "%ADD10C,0.200*%\n"
        + "D10*\n"
        + "X010000Y020000D03*\n"
        + "M02*\n",
        encoding="utf-8",
    )
    mirrored_pad = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    assert plain_pad.id != mirrored_pad.id
