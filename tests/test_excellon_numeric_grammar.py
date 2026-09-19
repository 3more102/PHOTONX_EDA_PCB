from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.excellon_routing.arc_commands import (
    parse_arc_route_command,
    parse_radius_arc_route_command,
)
from photonx_eda_pcb.excellon_routing.commands import parse_linear_route_command
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.parsers.excellon_parts.coordinates import parse_excellon_xy
from photonx_eda_pcb.parsers.excellon_parts.slots import parse_slot_command
from photonx_eda_pcb.parsers.excellon_parts.tool_table import parse_tool_definition
from photonx_eda_pcb.preflight import preflight


@pytest.mark.parametrize(
    ("parser", "text"),
    [
        (parse_linear_route_command, "G01X."),
        (parse_linear_route_command, "G01X1..2"),
        (parse_arc_route_command, "G03X1Y2I."),
        (parse_arc_route_command, "G03X1..2Y2I0J1"),
        (parse_radius_arc_route_command, "G03X1Y2A."),
        (parse_radius_arc_route_command, "G03X1Y2A1..0"),
        (parse_slot_command, "X1Y2G85X.Y4"),
        (parse_excellon_xy, "X."),
        (parse_excellon_xy, "X1..2Y3"),
        (parse_tool_definition, "T01C."),
        (parse_tool_definition, "T01C1..0"),
    ],
)
def test_helpers_reject_malformed_numeric_tokens(parser, text):
    with pytest.raises(ValueError):
        parser(text)


def test_helpers_keep_supported_explicit_decimal_forms():
    assert parse_linear_route_command("G01X.5Y1.") == ("G01", ".5", "1.")
    assert parse_excellon_xy("X+.5Y-1.") == {"x": "+.5", "y": "-1."}
    assert parse_tool_definition("T01C.8").diameter == pytest.approx(0.8)


def test_malformed_coordinate_disables_permissive_file_geometry(tmp_path: Path):
    path = tmp_path / "bad-coordinate.drl"
    path.write_text(
        "M48\n"
        "METRIC\n"
        "T01C0.8\n"
        "%\n"
        "T01\n"
        "X1.0Y1.0\n"
        "X1..0Y2.0\n"
        "X3.0Y3.0\n"
        "M30\n",
        encoding="utf-8",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []
    assert any(d.code == "INVALID_EXCELLON_COORDINATE" for d in result.diagnostics)


def test_malformed_tool_definition_disables_permissive_file_geometry(tmp_path: Path):
    path = tmp_path / "bad-tool.drl"
    path.write_text(
        "M48\n"
        "METRIC\n"
        "T01C.\n"
        "%\n"
        "T01\n"
        "X1.0Y1.0\n"
        "M30\n",
        encoding="utf-8",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert any(
        d.code == "INVALID_EXCELLON_TOOL_DEFINITION" for d in result.diagnostics
    )


def test_non_finite_explicit_decimal_fails_closed(tmp_path: Path):
    huge = "9" * 400 + ".0"
    path = tmp_path / "overflow-coordinate.drl"
    path.write_text(
        "M48\n"
        "METRIC\n"
        "T01C0.8\n"
        "%\n"
        "T01\n"
        f"X{huge}Y1.0\n"
        "M30\n",
        encoding="utf-8",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert any(d.code == "INVALID_EXCELLON_NUMERIC" for d in result.diagnostics)


def test_malformed_route_numeric_is_controlled_parse_error(tmp_path: Path):
    path = tmp_path / "bad-route.drl"
    path.write_text(
        "M48\n"
        "METRIC\n"
        "T01C0.8\n"
        "%\n"
        "T01\n"
        "G00X0Y0\n"
        "M15\n"
        "G01X1..0Y2\n"
        "M16\n"
        "M30\n",
        encoding="utf-8",
    )

    with pytest.raises(ParseError, match="malformed linear route command"):
        ExcellonParser(strict=True).parse(path)


def test_malformed_arc_numeric_fails_closed_in_preflight(tmp_path: Path):
    path = tmp_path / "bad-arc.drl"
    path.write_text(
        "M48\n"
        "METRIC\n"
        "T01C0.8\n"
        "%\n"
        "T01\n"
        "G00X0Y0\n"
        "M15\n"
        "G03X1Y1I.J0\n"
        "M16\n"
        "M30\n",
        encoding="utf-8",
    )

    report = preflight(path)

    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_EXCELLON_ROUTE_ARC_SYNTAX" in blocker
        for blocker in report.strict_blockers
    )


def test_production_parser_accepts_leading_and_trailing_decimal_points(tmp_path: Path):
    path = tmp_path / "valid-decimals.drl"
    path.write_text(
        "M48\n"
        "METRIC\n"
        "T01C.8\n"
        "%\n"
        "T01\n"
        "G00X.5Y.5\n"
        "M15\n"
        "G01X1.Y.5\n"
        "M16\n"
        "M30\n",
        encoding="utf-8",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.routes) == 1
    assert result.routes[0].points[0] == pytest.approx((0.5, 0.5))
    assert result.routes[0].points[-1] == pytest.approx((1.0, 0.5))
