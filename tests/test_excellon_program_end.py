import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.parsers.excellon_parts.commands import (
    classify_excellon_command,
    is_program_end,
)


HEADER = "M48\nMETRIC\nT01C0.800\n%\nT01\n"


@pytest.mark.parametrize("terminator", ["M30", "M00"])
def test_program_end_ignores_trailing_geometry(tmp_path, terminator):
    path = tmp_path / "terminated.drl"
    path.write_text(
        HEADER
        + "X1.000Y1.000\n"
        + terminator
        + "\n"
        + "X2.000Y2.000\n",
        encoding="utf-8",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.drills) == 1
    assert result.drills[0].center.x == pytest.approx(1.0)
    assert result.drills[0].center.y == pytest.approx(1.0)


@pytest.mark.parametrize("terminator", ["M30", "M00"])
def test_command_classifier_recognizes_program_end_forms(terminator):
    assert is_program_end(terminator)
    assert classify_excellon_command(terminator) == "eof"


@pytest.mark.parametrize(
    "not_terminator",
    [
        "M30X10Y20",
        "M00X10Y20",
        "M30X.",
        "M00Y+",
        "M30X1..2",
        "M00X1Y2.3.4",
    ],
)
def test_extended_program_end_dialects_are_not_accepted(not_terminator):
    assert not is_program_end(not_terminator)
    assert classify_excellon_command(not_terminator) == "unknown"


@pytest.mark.parametrize("terminator", ["M30", "M00"])
def test_program_end_with_route_tool_down_remains_fail_closed(tmp_path, terminator):
    path = tmp_path / "unterminated_route.drl"
    path.write_text(
        HEADER
        + "G00X1.000Y1.000\n"
        + "M15\n"
        + "G01X2.000Y1.000\n"
        + terminator
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ParseError, match="EOF while route tool is down"):
        ExcellonParser(strict=True).parse(path)

    permissive = ExcellonParser(strict=False).parse(path)
    assert permissive.drills == []
    assert permissive.slots == []
    assert permissive.routes == []
    assert any(
        diagnostic.code == "EXCELLON_ROUTE_UNTERMINATED"
        for diagnostic in permissive.diagnostics
    )


@pytest.mark.parametrize("statement", ["M30X10Y20", "M00X10Y20"])
def test_extended_stop_statement_fails_closed_in_strict_parser(tmp_path, statement):
    path = tmp_path / "extended-stop.drl"
    path.write_text(HEADER + "X1Y1\n" + statement + "\n", encoding="utf-8")

    with pytest.raises(ParseError, match="unrecognized Excellon statement"):
        ExcellonParser(strict=True).parse(path)


def test_trailing_unit_or_tool_records_after_program_end_are_ignored(tmp_path):
    path = tmp_path / "trailing-control.drl"
    path.write_text(
        HEADER
        + "X1Y1\n"
        + "M30\n"
        + "INCH\n"
        + "T02C0.050\n"
        + "T02\n"
        + "X2Y2\n",
        encoding="utf-8",
    )

    result = ExcellonParser(strict=True).parse(path)
    assert len(result.drills) == 1
    assert result.drills[0].center.x == pytest.approx(0.001)
    assert result.drills[0].center.y == pytest.approx(0.001)
