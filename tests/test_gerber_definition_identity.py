from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


HEADER = """%FSLAX24Y24*%
%MOMM*%
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "definitions.gtl"
    path.write_text(HEADER + body, encoding="utf-8")
    return path


@pytest.mark.parametrize("code", ["9", "2147483648"])
def test_aperture_identifier_must_use_spec_range(tmp_path: Path, code: str):
    path = _write(
        tmp_path,
        f"%ADD{code}C,0.500*%\nM02*\n",
    )

    with pytest.raises(ParseError, match="must be in 10\\.\\.2147483647"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_aperture_identifier_cannot_be_reassigned(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,0.500*%\n"
        "%ADD10R,0.500X0.250*%\n"
        "M02*\n",
    )

    with pytest.raises(ParseError, match="D10 cannot be re-assigned"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_aperture_identifier_cannot_change_from_standard_to_macro(tmp_path: Path):
    path = _write(
        tmp_path,
        "%AMDOT*1,1,0.250,0,0*%\n"
        "%ADD10C,0.500*%\n"
        "%ADD10DOT*%\n"
        "M02*\n",
    )

    with pytest.raises(ParseError, match="D10 cannot be re-assigned"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_duplicate_aperture_identifier_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "%ADD10R,0.500X0.250*%\n"
        "X020000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert result.tracks == []
    assert result.regions == []
    assert any(
        diagnostic.code == "DUPLICATE_GERBER_APERTURE_ID"
        for diagnostic in result.diagnostics
    )


def test_aperture_macro_name_cannot_reuse_standard_template(tmp_path: Path):
    path = _write(
        tmp_path,
        "%AMC*1,1,0.250,0,0*%\nM02*\n",
    )

    with pytest.raises(ParseError, match="conflicts with a standard aperture template"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_aperture_macro_name_must_be_unique(tmp_path: Path):
    path = _write(
        tmp_path,
        "%AMDOT*1,1,0.250,0,0*%\n"
        "%AMDOT*1,1,0.500,0,0*%\n"
        "M02*\n",
    )

    with pytest.raises(ParseError, match="aperture macro name 'DOT' must be unique"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_duplicate_macro_name_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%AMDOT*1,1,0.250,0,0*%\n"
        "%ADD10DOT*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "%AMDOT*1,1,0.500,0,0*%\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert result.tracks == []
    assert result.regions == []
    assert any(
        diagnostic.code == "DUPLICATE_GERBER_APERTURE_MACRO"
        for diagnostic in result.diagnostics
    )


def test_preflight_blocks_duplicate_aperture_identifier(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,0.500*%\n"
        "%ADD10R,0.500X0.250*%\n"
        "M02*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "DUPLICATE_GERBER_APERTURE_ID" in blocker
        for blocker in report.strict_blockers
    )
