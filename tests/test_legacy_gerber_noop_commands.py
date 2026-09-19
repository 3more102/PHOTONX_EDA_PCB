from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


BASE = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,0.200*%
D10*
"""


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(BASE + body, encoding="utf-8")
    return path


@pytest.mark.parametrize("command", ["%ASAXBY*%", "%ASAYBX*%"])
def test_axis_select_has_no_cad_to_cam_geometry_effect(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        "axis_select.gtl",
        command
        + "\n"
        + "X010000Y020000D02*\n"
        + "X030000Y040000D01*\n"
        + "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 1
    track = result.tracks[0]
    assert (track.start.x, track.start.y) == pytest.approx((1.0, 2.0))
    assert (track.end.x, track.end.y) == pytest.approx((3.0, 4.0))
    assert any(
        d.code == "GERBER_AXIS_SELECT_OUTPUT_DEVICE_ONLY"
        for d in result.diagnostics
    )


def test_invalid_axis_select_is_rejected(tmp_path: Path):
    path = _write(
        tmp_path,
        "bad_as.gtl",
        "%ASAXBX*%\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(ParseError, match="must be AXBY or AYBX"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_duplicate_axis_select_is_rejected(tmp_path: Path):
    path = _write(
        tmp_path,
        "duplicate_as.gtl",
        "%ASAXBY*%\n"
        "%ASAYBX*%\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(ParseError, match="may only be declared once"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_late_axis_select_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "late_as.gtl",
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%ASAYBX*%\n"
        "X020000Y000000D01*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(d.code == "LATE_GERBER_AXIS_SELECT" for d in result.diagnostics)


def test_image_name_is_preserved_as_non_geometric_comment(tmp_path: Path):
    path = _write(
        tmp_path,
        "image_name.gtl",
        "%INTop_Copper*%\n"
        "X010000Y020000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    assert any(
        d.code == "GERBER_IMAGE_NAME_COMMENT"
        and "Top_Copper" in d.message
        for d in result.diagnostics
    )


def test_duplicate_image_name_is_rejected(tmp_path: Path):
    path = _write(
        tmp_path,
        "duplicate_in.gtl",
        "%INOne*%\n"
        "%INTwo*%\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(ParseError, match="may only be declared once"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_load_name_can_repeat_without_geometry_effect(tmp_path: Path):
    path = _write(
        tmp_path,
        "load_name.gtl",
        "%LNFirst_section*%\n"
        "X000000Y000000D03*\n"
        "%LNSecond_section*%\n"
        "X010000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 2
    names = [
        d.message
        for d in result.diagnostics
        if d.code == "GERBER_LOAD_NAME_COMMENT"
    ]
    assert names == [
        "legacy LN section name: First_section",
        "legacy LN section name: Second_section",
    ]


def test_g55_prepare_flash_is_noop(tmp_path: Path):
    path = _write(
        tmp_path,
        "g55.gtl",
        "G55*\n"
        "X010000Y020000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    assert any(
        d.code == "GERBER_PREPARE_FLASH_IGNORED"
        for d in result.diagnostics
    )


def test_m01_optional_stop_is_noop_and_parsing_continues(tmp_path: Path):
    path = _write(
        tmp_path,
        "m01.gtl",
        "X000000Y000000D03*\n"
        "M01*\n"
        "X010000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 2
    assert any(
        d.code == "GERBER_OPTIONAL_STOP_IGNORED"
        for d in result.diagnostics
    )


@pytest.mark.parametrize("stop", ["M00*", "M02*"])
def test_program_stop_terminates_parsing(stop: str, tmp_path: Path):
    path = _write(
        tmp_path,
        "stop.gtl",
        "X000000Y000000D03*\n"
        + stop
        + "\n"
        + "X010000Y000000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    assert (result.pads[0].center.x, result.pads[0].center.y) == pytest.approx(
        (0.0, 0.0)
    )
