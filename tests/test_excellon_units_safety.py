from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.preflight import preflight


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "top.drl"
    path.write_text(text, encoding="utf-8")
    return path


def test_tool_definition_before_units_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "T01C0.600\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n",
    )

    with pytest.raises(ParseError, match="tool diameter encountered before explicit"):
        ExcellonParser(strict=True).parse(path)


def test_undeclared_units_suppress_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "T01C0.600\n"
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
        diagnostic.code == "EXCELLON_UNITS_UNDECLARED"
        for diagnostic in result.diagnostics
    )


def test_late_unit_declaration_does_not_reenable_suppressed_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "T01C0.600\n"
        "METRIC\n"
        "T01C0.600\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []


@pytest.mark.parametrize(
    ("unit", "tool_def", "expected_diameter_mm", "coordinate", "expected_x_mm"),
    [
        ("METRIC", "T01C0.600", 0.6, "X1.000Y1.000", 1.0),
        ("INCH", "T01C0.010", 0.254, "X1.000Y1.000", 25.4),
    ],
)
def test_explicit_units_keep_tool_and_coordinate_scaling(
    tmp_path: Path,
    unit: str,
    tool_def: str,
    expected_diameter_mm: float,
    coordinate: str,
    expected_x_mm: float,
):
    path = _write(
        tmp_path,
        "M48\n"
        + unit
        + "\n"
        + tool_def
        + "\n"
        "%\n"
        "T01\n"
        + coordinate
        + "\n"
        "M30\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.drills) == 1
    assert result.drills[0].diameter == pytest.approx(expected_diameter_mm)
    assert result.drills[0].center.x == pytest.approx(expected_x_mm)


def test_preflight_blocks_tool_definition_before_units(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "T01C0.600\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "EXCELLON_UNITS_UNDECLARED" in blocker
        for blocker in report.strict_blockers
    )


@pytest.mark.parametrize(
    ("first_units", "tool_def", "second_units"),
    [
        ("METRIC", "T01C0.600", "INCH"),
        ("INCH", "T01C0.010", "METRIC"),
        ("M71", "T01C0.600", "M72"),
        ("M72", "T01C0.010", "M71"),
    ],
)
def test_conflicting_units_fail_closed_in_strict_mode(
    tmp_path: Path,
    first_units: str,
    tool_def: str,
    second_units: str,
):
    path = _write(
        tmp_path,
        "M48\n"
        + first_units
        + "\n"
        + tool_def
        + "\n"
        + second_units
        + "\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n",
    )

    with pytest.raises(ParseError, match="conflicting Excellon unit declaration"):
        ExcellonParser(strict=True).parse(path)


def test_conflicting_units_clear_and_suppress_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "METRIC\n"
        "T01C0.600\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "INCH\n"
        "X2.000Y2.000\n"
        "M30\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []
    assert any(
        diagnostic.code == "CONFLICTING_EXCELLON_UNITS"
        for diagnostic in result.diagnostics
    )


def test_same_unit_redeclaration_remains_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "METRIC\n"
        "M71\n"
        "T01C0.600\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.drills) == 1
    assert result.drills[0].diameter == pytest.approx(0.6)
    assert result.drills[0].center.x == pytest.approx(1.0)


def test_preflight_blocks_conflicting_excellon_units(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "METRIC\n"
        "T01C0.600\n"
        "INCH\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "CONFLICTING_EXCELLON_UNITS" in blocker
        for blocker in report.strict_blockers
    )
