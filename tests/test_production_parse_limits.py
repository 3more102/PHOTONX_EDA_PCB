import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.common.limits import ParseLimits
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


def _write(tmp_path, name: str, body: str):
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


@pytest.mark.parametrize("strict", [True, False])
def test_excellon_enforces_physical_line_length_before_parsing(tmp_path, strict):
    path = _write(
        tmp_path,
        "board.drl",
        "M48\nMETRIC\n;123456789\nT01C0.8\n%\nT01\nX1Y1\nM30\n",
    )
    parser = ExcellonParser(
        strict=strict,
        limits=ParseLimits(max_lines=100, max_line_length=8),
    )

    with pytest.raises(ParseError, match=r"board\.drl:3: input line exceeds maximum length"):
        parser.parse(path)


def test_excellon_enforces_physical_line_count(tmp_path):
    path = _write(tmp_path, "board.drl", "M48\nMETRIC\n")
    parser = ExcellonParser(
        limits=ParseLimits(max_lines=1, max_line_length=100),
    )

    with pytest.raises(ParseError, match=r"board\.drl:2: input exceeds maximum line count"):
        parser.parse(path)


@pytest.mark.parametrize("strict", [True, False])
def test_gerber_enforces_physical_line_length_before_tokenization(tmp_path, strict):
    path = _write(
        tmp_path,
        "top.gtl",
        "%MOMM*%\n%FSLAX24Y24*%\nM02*\n",
    )
    parser = GerberRS274XParser(
        "F.Cu",
        strict=strict,
        limits=ParseLimits(max_lines=100, max_line_length=8),
    )

    with pytest.raises(ParseError, match=r"top\.gtl:2: input line exceeds maximum length"):
        parser.parse(path)


def test_gerber_enforces_physical_line_count(tmp_path):
    path = _write(
        tmp_path,
        "top.gtl",
        "%MOMM*%\n%FSLAX24Y24*%\nM02*\n",
    )
    parser = GerberRS274XParser(
        "F.Cu",
        limits=ParseLimits(max_lines=2, max_line_length=100),
    )

    with pytest.raises(ParseError, match=r"top\.gtl:3: input exceeds maximum line count"):
        parser.parse(path)


def test_excellon_streaming_path_preserves_valid_parse(tmp_path):
    path = _write(
        tmp_path,
        "valid.drl",
        "M48\nMETRIC\nT01C0.8\n%\nT01\nX1.0Y2.0\nM30\n",
    )
    result = ExcellonParser(
        limits=ParseLimits(max_lines=20, max_line_length=40),
    ).parse(path)

    assert len(result.drills) == 1
    assert result.drills[0].center.x == pytest.approx(1.0)
    assert result.drills[0].center.y == pytest.approx(2.0)
