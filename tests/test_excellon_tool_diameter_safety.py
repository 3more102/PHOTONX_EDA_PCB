from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.preflight import preflight


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "top.drl"
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("unit", "tool_def"),
    [
        ("METRIC", "T01C0.000"),
        ("INCH", "T01C0.000"),
    ],
)
def test_zero_diameter_tool_fails_closed_in_strict_mode(
    tmp_path: Path,
    unit: str,
    tool_def: str,
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
        "X1.000Y1.000\n"
        "M30\n",
    )

    with pytest.raises(ParseError, match="tool diameter must be positive"):
        ExcellonParser(strict=True).parse(path)


def test_zero_diameter_tool_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "METRIC\n"
        "T01C0.000\n"
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
        diagnostic.code == "INVALID_EXCELLON_TOOL_DIAMETER"
        for diagnostic in result.diagnostics
    )


def test_late_zero_diameter_tool_clears_prior_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "METRIC\n"
        "T01C0.600\n"
        "T02C0.000\n"
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
    ("unit", "tool_def", "expected_diameter_mm"),
    [
        ("METRIC", "T01C0.600", 0.6),
        ("INCH", "T01C0.010", 0.254),
    ],
)
def test_positive_tool_diameters_remain_supported(
    tmp_path: Path,
    unit: str,
    tool_def: str,
    expected_diameter_mm: float,
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
        "X1.000Y1.000\n"
        "M30\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.drills) == 1
    assert result.drills[0].diameter == pytest.approx(expected_diameter_mm)


def test_preflight_blocks_zero_diameter_tool(tmp_path: Path):
    path = _write(
        tmp_path,
        "M48\n"
        "METRIC\n"
        "T01C0.000\n"
        "%\n"
        "T01\n"
        "X1.000Y1.000\n"
        "M30\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_EXCELLON_TOOL_DIAMETER" in blocker
        for blocker in report.strict_blockers
    )
