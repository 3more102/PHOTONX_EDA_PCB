from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_parts.step_repeat import parse_step_repeat
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


BASE = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,0.500*%
D10*
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "panel.gtl"
    path.write_text(BASE + body + "M02*\n", encoding="utf-8")
    return path


@pytest.mark.parametrize(
    "statement",
    [
        "%SRX٢Y1I10J0*%",
        "%SRX2Y1I.J0*%",
        "%SRX2Y1I1..0J0*%",
    ],
)
def test_step_repeat_helper_rejects_non_ascii_or_malformed_numeric_tokens(
    statement: str,
):
    with pytest.raises(ValueError):
        parse_step_repeat(statement)


def test_step_repeat_helper_preserves_supported_decimal_forms():
    assert parse_step_repeat("%SRX2Y3I.5J1.*%") == {
        "x": 2,
        "y": 3,
        "i": 0.5,
        "j": 1.0,
    }


def test_step_repeat_helper_rejects_non_finite_offsets():
    huge = "9" * 400 + ".0"

    with pytest.raises(ValueError, match="non-finite step-repeat offset"):
        parse_step_repeat(f"%SRX2Y1I{huge}J0*%")


@pytest.mark.parametrize(
    "statement",
    [
        "%SRX٢Y1I10J0*%",
        "%SRX2Y1I.J0*%",
        "%SRX2Y1I1..0J0*%",
    ],
)
def test_invalid_step_repeat_numeric_grammar_fails_closed_in_strict_mode(
    tmp_path: Path,
    statement: str,
):
    path = _write(
        tmp_path,
        statement + "\n"
        "X010000Y010000D03*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="invalid Gerber step-and-repeat",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_non_finite_step_repeat_offset_suppresses_permissive_file_geometry(
    tmp_path: Path,
):
    huge = "9" * 400 + ".0"
    path = _write(
        tmp_path,
        "X005000Y005000D03*\n"
        f"%SRX2Y1I{huge}J0*%\n"
        "X010000Y010000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(
        diagnostic.code == "INVALID_GERBER_STEP_REPEAT"
        for diagnostic in result.diagnostics
    )
