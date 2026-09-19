from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.parsers.excellon_parts.tool_table import parse_tool_definition
from photonx_eda_pcb.preflight import preflight


UNICODE_TOOL = "T\u0660\u0661"


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "tool-id.drl"
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize("tool_digits", ["\u0660\u0661", "\uff10\uff11", "\u0966\u0967"])
def test_low_level_tool_parser_rejects_unicode_digit_lookalikes(tool_digits: str):
    with pytest.raises(ValueError, match="invalid tool definition"):
        parse_tool_definition(f"T{tool_digits}C0.800")


def test_ascii_tool_identifier_remains_supported():
    tool = parse_tool_definition("T01C0.800")

    assert tool.number == 1
    assert tool.diameter == pytest.approx(0.8)


def test_unicode_tool_definition_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "METRIC\n"
        f"{UNICODE_TOOL}C0.800\n"
        "%\n"
        f"{UNICODE_TOOL}\n"
        "X1.000Y1.000\n"
        "M30\n",
    )

    with pytest.raises(ParseError, match="malformed Excellon tool definition"):
        ExcellonParser(strict=True).parse(path)


def test_unicode_tool_definition_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "METRIC\n"
        f"{UNICODE_TOOL}C0.800\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []
    assert any(
        diagnostic.code == "INVALID_EXCELLON_TOOL_DEFINITION"
        for diagnostic in result.diagnostics
    )


def test_unicode_tool_selection_fails_closed_and_clears_prior_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "METRIC\n"
        "T01C0.800\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        f"{UNICODE_TOOL}\n"
        "X2.000Y2.000\n"
        "M30\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []
    assert any(
        diagnostic.code == "INVALID_EXCELLON_TOOL_SELECTION"
        for diagnostic in result.diagnostics
    )


def test_unicode_tool_selection_is_rejected_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "METRIC\n"
        "T01C0.800\n"
        "%\n"
        f"{UNICODE_TOOL}\n"
        "X1.000Y1.000\n"
        "M30\n",
    )

    with pytest.raises(ParseError, match="malformed Excellon tool selection"):
        ExcellonParser(strict=True).parse(path)


def test_preflight_blocks_unicode_tool_selection(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "METRIC\n"
        "T01C0.800\n"
        "%\n"
        f"{UNICODE_TOOL}\n"
        "X1.000Y1.000\n"
        "M30\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_EXCELLON_TOOL_SELECTION" in blocker
        for blocker in report.strict_blockers
    )
