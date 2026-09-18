from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "units.gtl"
    path.write_text(body, encoding="utf-8")
    return path


def test_dimensional_data_before_units_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    with pytest.raises(ParseError, match="before explicit MO/G70/G71"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_undeclared_units_suppress_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(
        diagnostic.code == "GERBER_UNITS_UNDECLARED"
        for diagnostic in result.diagnostics
    )


def test_late_unit_declaration_does_not_reenable_suppressed_geometry(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%ADD10C,0.500*%\n"
        "%MOMM*%\n"
        "%ADD11C,0.500*%\n"
        "D11*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []


@pytest.mark.parametrize(
    ("unit_command", "aperture", "coordinate", "diameter_mm", "x_mm"),
    [
        ("G71*", "0.500", "X010000Y000000D03*", 0.5, 1.0),
        ("G70*", "0.010", "X010000Y000000D03*", 0.254, 25.4),
    ],
)
def test_legacy_g70_g71_are_explicit_unit_declarations(
    tmp_path: Path,
    unit_command: str,
    aperture: str,
    coordinate: str,
    diameter_mm: float,
    x_mm: float,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        + unit_command
        + "\n"
        + f"%ADD10C,{aperture}*%\n"
        + "D10*\n"
        + coordinate
        + "\nM02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    assert result.pads[0].x == pytest.approx(diameter_mm)
    assert result.pads[0].center.x == pytest.approx(x_mm)


def test_conflicting_unit_switch_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "%MOIN*%\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="unit mode changed"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_conflicting_unit_switch_clears_prior_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "%MOIN*%\n"
        "X020000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(
        diagnostic.code == "CONFLICTING_GERBER_UNITS"
        for diagnostic in result.diagnostics
    )


def test_duplicate_same_unit_declaration_remains_tolerated(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1


@pytest.mark.parametrize(
    ("body", "expected_code"),
    [
        (
            "%FSLAX24Y24*%\n"
            "%ADD10C,0.500*%\n"
            "M02*\n",
            "GERBER_UNITS_UNDECLARED",
        ),
        (
            "%FSLAX24Y24*%\n"
            "%MOMM*%\n"
            "%MOIN*%\n"
            "M02*\n",
            "CONFLICTING_GERBER_UNITS",
        ),
    ],
)
def test_preflight_blocks_unsafe_unit_semantics(
    tmp_path: Path,
    body: str,
    expected_code: str,
):
    path = _write(tmp_path, body)

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(expected_code in blocker for blocker in report.strict_blockers)
