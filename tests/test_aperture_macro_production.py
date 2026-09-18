from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "macro.gtl"
    path.write_text(text, encoding="utf-8")
    return path


def test_single_circle_macro_flash_is_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMROUND*1,1,$1,0,0*%\n"
        "%ADD10ROUND,0.800*%\n"
        "D10*\n"
        "X010000Y020000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu").parse(path)

    assert len(result.pads) == 1
    pad = result.pads[0]
    assert pad.shape == "C"
    assert pad.size_x == pytest.approx(0.8)
    assert pad.size_y == pytest.approx(0.8)


def test_single_circle_macro_can_be_used_for_linear_draw(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMTRACE*1,1,$1,0,0*%\n"
        "%ADD10TRACE,0.250*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu").parse(path)

    assert len(result.tracks) == 1
    assert result.tracks[0].width == pytest.approx(0.25)


def test_circle_macro_respects_active_inch_units(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOIN*%\n"
        "%AMROUND*1,1,$1,0,0*%\n"
        "%ADD10ROUND,0.010*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu").parse(path)

    assert result.pads[0].size_x == pytest.approx(0.254)


def test_complex_macro_remains_fail_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMBOX*21,1,$1,$2,0,0,0*%\n"
        "%ADD10BOX,1.0X2.0*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_complex_macro_is_diagnostic_in_permissive_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMBOX*21,1,$1,$2,0,0,0*%\n"
        "%ADD10BOX,1.0X2.0*%\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert any(
        d.code == "UNSUPPORTED_GERBER_APERTURE_MACRO"
        for d in result.diagnostics
    )
