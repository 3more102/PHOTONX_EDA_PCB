from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.preflight import preflight


HEADER = "M48\nMETRIC\nT01C0.800\n%\n"


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "xnc_safety.drl"
    path.write_text(text, encoding="utf-8")
    return path


def test_m30_rejects_trailing_data_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        HEADER
        + "T01\n"
        + "X1.000Y1.000\n"
        + "M30\n"
        + "X2.000Y2.000\n",
    )

    with pytest.raises(ParseError, match="data after M30"):
        ExcellonParser(strict=True).parse(path)


def test_m30_trailing_data_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        HEADER
        + "T01\n"
        + "X1.000Y1.000\n"
        + "M30\n"
        + "X2.000Y2.000\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []
    assert any(
        diagnostic.code == "INVALID_EXCELLON_DATA_AFTER_M30"
        for diagnostic in result.diagnostics
    )


def test_blank_lines_and_comments_after_m30_remain_non_geometric(tmp_path: Path):
    path = _write(
        tmp_path,
        HEADER
        + "T01\n"
        + "X1.000Y1.000\n"
        + "M30\n"
        + "\n"
        + "; generator footer\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.drills) == 1


def test_undefined_tool_selection_fails_immediately_in_strict_mode(tmp_path: Path):
    path = _write(tmp_path, HEADER + "T02\nM30\n")

    with pytest.raises(ParseError, match="undefined Excellon tool selection T02"):
        ExcellonParser(strict=True).parse(path)


def test_undefined_tool_selection_clears_prior_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        HEADER
        + "T01\n"
        + "X1.000Y1.000\n"
        + "T02\n"
        + "M30\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert any(
        diagnostic.code == "INVALID_EXCELLON_TOOL_SELECTION"
        for diagnostic in result.diagnostics
    )


def test_duplicate_tool_definition_fails_closed(tmp_path: Path):
    text = "M48\nMETRIC\nT01C0.800\nT01C0.900\n%\nM30\n"
    path = _write(tmp_path, text)

    with pytest.raises(ParseError, match="duplicate Excellon tool definition T01"):
        ExcellonParser(strict=True).parse(path)

    result = ExcellonParser(strict=False).parse(path)
    assert result.drills == []
    assert any(
        diagnostic.code == "INVALID_EXCELLON_TOOL_REDEFINITION"
        for diagnostic in result.diagnostics
    )


def test_nonfinite_tool_diameter_becomes_parser_error(tmp_path: Path):
    diameter = "9" * 400
    path = _write(tmp_path, f"M48\nMETRIC\nT01C{diameter}\n%\nM30\n")

    with pytest.raises(ParseError, match="tool diameter must be positive and finite"):
        ExcellonParser(strict=True).parse(path)


def test_malformed_tool_diameter_uses_lexical_definition_error(tmp_path: Path):
    path = _write(tmp_path, "M48\nMETRIC\nT01C.\n%\nM30\n")

    with pytest.raises(ParseError, match="malformed Excellon tool definition"):
        ExcellonParser(strict=True).parse(path)


@pytest.mark.parametrize(
    ("text", "code"),
    [
        (
            HEADER + "T01\nX1.000Y1.000\nM30\nX2.000Y2.000\n",
            "INVALID_EXCELLON_DATA_AFTER_M30",
        ),
        (HEADER + "T02\nM30\n", "INVALID_EXCELLON_TOOL_SELECTION"),
        (
            "M48\nMETRIC\nT01C0.800\nT01C0.900\n%\nM30\n",
            "INVALID_EXCELLON_TOOL_REDEFINITION",
        ),
        ("M48\nMETRIC\nT01C.\n%\nM30\n", "INVALID_EXCELLON_TOOL_DEFINITION"),
    ],
)
def test_preflight_blocks_xnc_eof_and_tool_table_violations(
    tmp_path: Path,
    text: str,
    code: str,
):
    path = _write(tmp_path, text)

    report = preflight(path)

    assert not report.ready_for_strict_reconstruction
    assert any(code in blocker for blocker in report.strict_blockers)
