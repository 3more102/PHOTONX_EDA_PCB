from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_excellon_parser_reuse_does_not_inherit_tool_table(tmp_path: Path):
    first = _write(
        tmp_path / "first.drl",
        "M48\n"
        "METRIC\n"
        "T01C0.600\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n",
    )
    second = _write(
        tmp_path / "second.drl",
        "M48\n"
        "METRIC\n"
        "%\n"
        "T01\n"
        "X2.000Y2.000\n"
        "M30\n",
    )

    parser = ExcellonParser(strict=True)
    assert len(parser.parse(first).drills) == 1

    with pytest.raises(ParseError):
        parser.parse(second)


def test_excellon_parser_reuse_clears_fail_closed_state(tmp_path: Path):
    invalid = _write(
        tmp_path / "invalid.drl",
        "M48\n"
        "METRIC\n"
        "T01C0.000\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n",
    )
    valid = _write(
        tmp_path / "valid.drl",
        "M48\n"
        "METRIC\n"
        "T02C0.800\n"
        "%\n"
        "T02\n"
        "X2.000Y3.000\n"
        "M30\n",
    )

    parser = ExcellonParser(strict=False)
    first = parser.parse(invalid)
    assert first.drills == []

    second = parser.parse(valid)
    assert len(second.drills) == 1
    assert second.drills[0].tool == "T02"


def test_gerber_parser_reuse_does_not_inherit_aperture_table(tmp_path: Path):
    first = _write(
        tmp_path / "first.gbr",
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,1.000*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )
    second = _write(
        tmp_path / "second.gbr",
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "D10*\n"
        "X020000Y020000D03*\n"
        "M02*\n",
    )

    parser = GerberRS274XParser("F.Cu", strict=True)
    assert len(parser.parse(first).pads) == 1

    with pytest.raises(ParseError):
        parser.parse(second)


def test_gerber_parser_reuse_clears_fail_closed_state(tmp_path: Path):
    invalid = _write(
        tmp_path / "invalid.gbr",
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TF.FilePolarity,Negative*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )
    valid = _write(
        tmp_path / "valid.gbr",
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD11C,0.500*%\n"
        "D11*\n"
        "X020000Y030000D03*\n"
        "M02*\n",
    )

    parser = GerberRS274XParser("F.Cu", strict=False)
    first = parser.parse(invalid)
    assert first.pads == []

    second = parser.parse(valid)
    assert len(second.pads) == 1
    assert second.pads[0].center.x == pytest.approx(2.0)
    assert second.pads[0].center.y == pytest.approx(3.0)
