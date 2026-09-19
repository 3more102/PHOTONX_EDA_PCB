import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.preflight import preflight


def _write_program(tmp_path, name: str, trailing: str = ""):
    path = tmp_path / name
    path.write_text(
        "M48\n"
        "METRIC\n"
        "T01C0.8\n"
        "%\n"
        "T01\n"
        "X1.0Y1.0\n"
        "M30\n"
        + trailing,
        encoding="utf-8",
    )
    return path


def test_m30_terminates_valid_excellon_program(tmp_path):
    path = _write_program(tmp_path, "valid.drl")
    result = ExcellonParser().parse(path)

    assert len(result.drills) == 1
    assert result.diagnostics == []


@pytest.mark.parametrize("trailing", ["X2.0Y2.0\n", "M30\n"])
def test_strict_parser_rejects_noncomment_data_after_m30(tmp_path, trailing):
    path = _write_program(tmp_path, "trailing.drl", trailing)

    with pytest.raises(ParseError, match="data after Excellon M30"):
        ExcellonParser().parse(path)


def test_blank_lines_and_comments_after_m30_remain_non_geometric(tmp_path):
    path = _write_program(tmp_path, "footer.drl", "\n; generator footer\n")

    result = ExcellonParser().parse(path)

    assert len(result.drills) == 1
    assert result.diagnostics == []


def test_permissive_parser_fails_closed_after_m30(tmp_path):
    path = _write_program(tmp_path, "trailing.drl", "X2.0Y2.0\n")

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []
    assert [d.code for d in result.diagnostics] == [
        "INVALID_EXCELLON_DATA_AFTER_M30"
    ]


def test_undefined_tool_selection_fails_closed(tmp_path):
    path = tmp_path / "undefined-tool.drl"
    path.write_text(
        "M48\nMETRIC\nT01C0.8\n%\nT02\nM30\n",
        encoding="utf-8",
    )

    with pytest.raises(ParseError, match="undefined Excellon tool selection T02"):
        ExcellonParser(strict=True).parse(path)

    result = ExcellonParser(strict=False).parse(path)
    assert result.drills == []
    assert [d.code for d in result.diagnostics] == [
        "INVALID_EXCELLON_TOOL_SELECTION"
    ]


def test_undefined_tool_selection_clears_prior_permissive_geometry(tmp_path):
    path = tmp_path / "undefined-after-hit.drl"
    path.write_text(
        "M48\nMETRIC\nT01C0.8\n%\nT01\nX1Y1\nT02\nM30\n",
        encoding="utf-8",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert [d.code for d in result.diagnostics] == [
        "INVALID_EXCELLON_TOOL_SELECTION"
    ]


def test_duplicate_tool_definition_fails_closed(tmp_path):
    path = tmp_path / "duplicate-tool.drl"
    path.write_text(
        "M48\nMETRIC\nT01C0.8\nT01C0.9\n%\nM30\n",
        encoding="utf-8",
    )

    with pytest.raises(ParseError, match="duplicate Excellon tool definition T01"):
        ExcellonParser(strict=True).parse(path)

    result = ExcellonParser(strict=False).parse(path)
    assert result.drills == []
    assert [d.code for d in result.diagnostics] == [
        "INVALID_EXCELLON_TOOL_REDEFINITION"
    ]


def test_tool_diameter_unit_conversion_must_remain_finite(tmp_path):
    path = tmp_path / "overflow-tool.drl"
    path.write_text(
        "M48\nINCH\nT01C" + ("9" * 400) + "\n%\nM30\n",
        encoding="utf-8",
    )

    with pytest.raises(ParseError, match="positive and finite"):
        ExcellonParser(strict=True).parse(path)

    result = ExcellonParser(strict=False).parse(path)
    assert result.drills == []
    assert [d.code for d in result.diagnostics] == [
        "INVALID_EXCELLON_TOOL_DIAMETER"
    ]


@pytest.mark.parametrize(
    ("text", "code"),
    [
        (
            "M48\nMETRIC\nT01C0.8\n%\nT01\nX1Y1\nM30\nX2Y2\n",
            "INVALID_EXCELLON_DATA_AFTER_M30",
        ),
        (
            "M48\nMETRIC\nT01C0.8\n%\nT02\nM30\n",
            "INVALID_EXCELLON_TOOL_SELECTION",
        ),
        (
            "M48\nMETRIC\nT01C0.8\nT01C0.9\n%\nM30\n",
            "INVALID_EXCELLON_TOOL_REDEFINITION",
        ),
    ],
)
def test_preflight_blocks_xnc_eof_and_tool_table_violations(
    tmp_path, text, code
):
    path = tmp_path / "preflight.drl"
    path.write_text(text, encoding="utf-8")

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(code in blocker for blocker in report.strict_blockers)
