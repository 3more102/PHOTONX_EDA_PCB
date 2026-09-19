import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.parsers.excellon_parts.commands import (
    classify_excellon_command,
    is_program_end,
)


HEADER = "M48\nMETRIC\nT01C0.800\n%\nT01\n"


@pytest.mark.parametrize(
    "terminator",
    ["M30", "M00", "M30X10.000Y20.000", "M00X10.000Y20.000", "M30Y20.000"],
)
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


@pytest.mark.parametrize(
    "terminator",
    ["M30", "M00", "M30X10.000Y20.000", "M00X10.000Y20.000", "M30Y20.000"],
)
def test_command_classifier_recognizes_program_end_forms(terminator):
    assert is_program_end(terminator)
    assert classify_excellon_command(terminator) == "eof"


@pytest.mark.parametrize("terminator", ["M30X.", "M00Y+", "M30X1..2", "M00X1Y2.3.4"])
def test_malformed_program_end_coordinates_are_not_accepted(terminator):
    assert not is_program_end(terminator)
    assert classify_excellon_command(terminator) == "unknown"


@pytest.mark.parametrize("terminator", ["M30", "M00", "M30X10Y20"])
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
