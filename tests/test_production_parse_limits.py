from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.common.limits import ParseLimits
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


def _write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize("strict", [True, False])
def test_gerber_line_budget_is_hard_safety_limit(tmp_path: Path, strict: bool):
    path = _write(
        tmp_path,
        "too-many-lines.gbr",
        "%FSLAX24Y24*%\n%MOMM*%\nM02*\n",
    )

    parser = GerberRS274XParser(
        "F.Cu",
        strict=strict,
        limits=ParseLimits(max_lines=2),
    )
    with pytest.raises(ParseError, match="maximum line count"):
        parser.parse(path)


def test_gerber_line_length_budget_is_enforced(tmp_path: Path):
    path = _write(tmp_path, "long-line.gbr", "%FSLAX24Y24*%\nM02*\n")

    parser = GerberRS274XParser(
        "F.Cu",
        limits=ParseLimits(max_line_length=8),
    )
    with pytest.raises(ParseError, match="maximum length"):
        parser.parse(path)


def test_gerber_aperture_budget_counts_unique_d_codes(tmp_path: Path):
    path = _write(
        tmp_path,
        "apertures.gbr",
        (
            "%FSLAX24Y24*%\n"
            "%MOMM*%\n"
            "%ADD10C,1.0*%\n"
            "%ADD11C,1.0*%\n"
            "M02*\n"
        ),
    )

    parser = GerberRS274XParser(
        "F.Cu",
        limits=ParseLimits(max_apertures=1),
    )
    with pytest.raises(ParseError, match="maximum aperture count"):
        parser.parse(path)


def test_gerber_aperture_macro_budget_is_enforced(tmp_path: Path):
    path = _write(
        tmp_path,
        "macros.gbr",
        "%AMA*1,1,1.0,0,0*%\n%AMB*1,1,1.0,0,0*%\nM02*\n",
    )

    parser = GerberRS274XParser(
        "F.Cu",
        limits=ParseLimits(max_aperture_macros=1),
    )
    with pytest.raises(ParseError, match="maximum aperture-macro count"):
        parser.parse(path)


def test_gerber_object_budget_bounds_stepwise_geometry_emission(tmp_path: Path):
    path = _write(
        tmp_path,
        "objects.gbr",
        (
            "%FSLAX24Y24*%\n"
            "%MOMM*%\n"
            "%ADD10C,1.0*%\n"
            "D10*\n"
            "X000000Y000000D03*\n"
            "X010000Y000000D03*\n"
            "M02*\n"
        ),
    )

    parser = GerberRS274XParser(
        "F.Cu",
        limits=ParseLimits(max_objects=1),
    )
    with pytest.raises(ParseError, match="maximum object count"):
        parser.parse(path)


@pytest.mark.parametrize("strict", [True, False])
def test_excellon_line_budget_is_hard_safety_limit(tmp_path: Path, strict: bool):
    path = _write(
        tmp_path,
        "too-many-lines.drl",
        "M48\nMETRIC\nM30\n",
    )

    parser = ExcellonParser(
        strict=strict,
        limits=ParseLimits(max_lines=2),
    )
    with pytest.raises(ParseError, match="maximum line count"):
        parser.parse(path)


def test_excellon_tool_budget_counts_unique_tool_definitions(tmp_path: Path):
    path = _write(
        tmp_path,
        "tools.drl",
        "M48\nMETRIC\nT01C0.800\nT02C0.900\n%\nM30\n",
    )

    parser = ExcellonParser(limits=ParseLimits(max_tools=1))
    with pytest.raises(ParseError, match="maximum tool count"):
        parser.parse(path)


def test_excellon_object_budget_bounds_drill_slot_route_outputs(tmp_path: Path):
    path = _write(
        tmp_path,
        "objects.drl",
        (
            "M48\n"
            "METRIC\n"
            "T01C0.800\n"
            "%\n"
            "T01\n"
            "X1.000Y1.000\n"
            "X2.000Y2.000\n"
            "M30\n"
        ),
    )

    parser = ExcellonParser(limits=ParseLimits(max_objects=1))
    with pytest.raises(ParseError, match="maximum object count"):
        parser.parse(path)
