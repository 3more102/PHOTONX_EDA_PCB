from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.gerber_parts.step_repeat import parse_step_repeat
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


HEADER = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,0.200*%
D10*
"""


def _write(tmp_path: Path, body: str, *, header: str = HEADER) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(header + body + "M02*\n", encoding="utf-8")
    return path


@pytest.mark.parametrize("token", [".", "1..0", "+", "1e2", "nan"])
def test_malformed_explicit_decimal_coordinate_fails_closed(
    tmp_path: Path,
    token: str,
):
    path = _write(tmp_path, f"X{token}Y020000D03*\n")

    with pytest.raises(ParseError, match="invalid Gerber coordinate value"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_non_finite_coordinate_fails_closed(tmp_path: Path):
    huge = "9" * 400 + ".0"
    path = _write(tmp_path, f"X{huge}Y020000D03*\n")

    with pytest.raises(ParseError, match="invalid Gerber coordinate value"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_coordinate_unit_conversion_overflow_fails_closed(tmp_path: Path):
    finite_but_overflowing_inch_value = "1" + ("0" * 307) + ".0"
    header = """%FSLAX24Y24*%
%MOIN*%
%ADD10C,0.010*%
D10*
"""
    path = _write(
        tmp_path,
        f"X{finite_but_overflowing_inch_value}Y0.0D03*\n",
        header=header,
    )

    with pytest.raises(ParseError, match="invalid Gerber coordinate value"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_permissive_invalid_coordinate_suppresses_complete_file_image(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "X010000Y010000D03*\n"
        "X1..0Y020000D03*\n"
        "X030000Y030000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.regions == []
    assert result.outline == []
    assert any(
        diagnostic.code == "INVALID_GERBER_COORDINATE"
        for diagnostic in result.diagnostics
    )


def test_invalid_arc_center_offset_uses_parser_diagnostic(tmp_path: Path):
    huge = "9" * 400 + ".0"
    path = _write(
        tmp_path,
        "G75*\n"
        "X010000Y000000D02*\n"
        f"G03X000000Y010000I{huge}J000000D01*\n",
    )

    with pytest.raises(ParseError, match="invalid Gerber coordinate value"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_invalid_region_coordinate_fails_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "G36*\n"
        "X000000Y000000D02*\n"
        "X1e2Y010000D01*\n"
        "G37*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.regions == []
    assert any(
        diagnostic.code == "INVALID_GERBER_COORDINATE"
        for diagnostic in result.diagnostics
    )


def test_preflight_blocks_invalid_gerber_coordinate(tmp_path: Path):
    path = _write(tmp_path, "X1..0Y020000D03*\n")

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_GERBER_COORDINATE" in blocker
        for blocker in report.strict_blockers
    )


@pytest.mark.parametrize(
    "definition",
    [
        "%ADD10C,{huge}*%",
        "%ADD10R,{huge}X0.250*%",
        "%ADD10O,0.500X{huge}*%",
        "%ADD10P,{huge}X6*%",
    ],
)
def test_non_finite_standard_aperture_modifiers_fail_closed(
    tmp_path: Path,
    definition: str,
):
    huge = ("9" * 400) + ".0"
    path = _write(
        tmp_path,
        "D10*\nX010000Y020000D03*\n",
        header="%FSLAX24Y24*%\n%MOMM*%\n" + definition.format(huge=huge) + "\n",
    )

    with pytest.raises(ParseError, match="standard aperture modifiers must be finite"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_standard_aperture_unit_conversion_overflow_fails_closed(tmp_path: Path):
    finite_but_overflowing_inch_value = "1" + ("0" * 307) + ".0"
    path = _write(
        tmp_path,
        "D10*\nX0.0Y0.0D03*\n",
        header=(
            "%FSLAX24Y24*%\n"
            "%MOIN*%\n"
            f"%ADD10C,{finite_but_overflowing_inch_value}*%\n"
        ),
    )

    with pytest.raises(ParseError, match="overflow after active-unit conversion"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_permissive_invalid_standard_aperture_is_diagnostic_and_skipped(
    tmp_path: Path,
):
    huge = ("9" * 400) + ".0"
    path = _write(
        tmp_path,
        "D10*\nX010000Y020000D03*\n",
        header=f"%FSLAX24Y24*%\n%MOMM*%\n%ADD10C,{huge}*%\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert result.regions == []
    assert any(
        diagnostic.code == "INVALID_GERBER_STANDARD_APERTURE"
        for diagnostic in result.diagnostics
    )


def test_preflight_blocks_non_finite_standard_aperture(tmp_path: Path):
    huge = ("9" * 400) + ".0"
    path = _write(
        tmp_path,
        "D10*\nX010000Y020000D03*\n",
        header=f"%FSLAX24Y24*%\n%MOMM*%\n%ADD10C,{huge}*%\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_GERBER_STANDARD_APERTURE" in blocker
        for blocker in report.strict_blockers
    )


@pytest.mark.parametrize(
    "statement",
    [
        "%SRX2Y1I.J0*%",
        "%SRX2Y1I1..0J0*%",
    ],
)
def test_step_repeat_helper_rejects_malformed_decimals(statement: str):
    with pytest.raises(ValueError, match="invalid step-repeat"):
        parse_step_repeat(statement)


def test_step_repeat_helper_rejects_non_finite_increment():
    huge = ("9" * 400) + ".0"

    with pytest.raises(ValueError, match="increments must be finite"):
        parse_step_repeat(f"%SRX2Y1I{huge}J0*%")


def test_step_repeat_unit_conversion_overflow_fails_closed(tmp_path: Path):
    finite_but_overflowing_inch_value = "1" + ("0" * 307) + ".0"
    header = """%FSLAX24Y24*%
%MOIN*%
%ADD10C,0.010*%
D10*
"""
    path = _write(
        tmp_path,
        f"%SRX2Y1I{finite_but_overflowing_inch_value}J0*%\n"
        "X0.0Y0.0D03*\n",
        header=header,
    )

    with pytest.raises(ParseError, match="step-and-repeat increments overflow"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_permissive_step_repeat_overflow_suppresses_complete_image(
    tmp_path: Path,
):
    finite_but_overflowing_inch_value = "1" + ("0" * 307) + ".0"
    header = """%FSLAX24Y24*%
%MOIN*%
%ADD10C,0.010*%
D10*
"""
    path = _write(
        tmp_path,
        "X0.0Y0.0D03*\n"
        f"%SRX2Y1I{finite_but_overflowing_inch_value}J0*%\n"
        "X1.0Y1.0D03*\n",
        header=header,
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.regions == []
    assert result.outline == []
    assert any(
        diagnostic.code == "INVALID_GERBER_STEP_REPEAT"
        for diagnostic in result.diagnostics
    )


def test_preflight_blocks_step_repeat_unit_conversion_overflow(tmp_path: Path):
    finite_but_overflowing_inch_value = "1" + ("0" * 307) + ".0"
    header = """%FSLAX24Y24*%
%MOIN*%
%ADD10C,0.010*%
D10*
"""
    path = _write(
        tmp_path,
        f"%SRX2Y1I{finite_but_overflowing_inch_value}J0*%\n"
        "X0.0Y0.0D03*\n",
        header=header,
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_GERBER_STEP_REPEAT" in blocker
        for blocker in report.strict_blockers
    )


def test_step_repeat_offset_arithmetic_overflow_fails_closed(tmp_path: Path):
    finite_increment = "1" + ("0" * 308) + ".0"
    path = _write(
        tmp_path,
        f"%SRX3Y1I{finite_increment}J0*%\n"
        "X0.0Y0.0D03*\n",
    )

    with pytest.raises(ParseError, match="step-and-repeat offset arithmetic"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)
