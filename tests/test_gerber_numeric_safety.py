from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
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


@pytest.mark.parametrize("token", [".", "1..0"])
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
        "X1..0Y010000D01*\n"
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
