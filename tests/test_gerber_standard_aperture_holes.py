from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


HEADER = """%FSLAX24Y24*%
%MOMM*%
"""


def _write(tmp_path: Path, aperture: str, body: str = "X010000Y020000D03*\n") -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(
        HEADER + aperture + "\nD10*\n" + body + "M02*\n",
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    ("definition", "shape", "x_mm", "y_mm"),
    [
        ("%ADD10C,0.500*%", "C", 0.5, 0.5),
        ("%ADD10R,0.500X0.250*%", "R", 0.5, 0.25),
        ("%ADD10O,0.500X0.250*%", "O", 0.5, 0.25),
    ],
)
def test_solid_standard_apertures_keep_exact_dimensions(
    tmp_path: Path,
    definition: str,
    shape: str,
    x_mm: float,
    y_mm: float,
):
    result = GerberRS274XParser("F.Cu", strict=True).parse(
        _write(tmp_path, definition)
    )

    assert len(result.pads) == 1
    pad = result.pads[0]
    assert pad.shape == shape
    assert pad.size_x == pytest.approx(x_mm)
    assert pad.size_y == pytest.approx(y_mm)


def test_circle_hole_modifier_is_not_misread_as_y_dimension(tmp_path: Path):
    path = _write(tmp_path, "%ADD10C,0.500X0.250*%")

    with pytest.raises(UnsupportedFeatureError, match="contains a 0.25 hole"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_rectangle_hole_modifier_fails_closed(tmp_path: Path):
    path = _write(tmp_path, "%ADD10R,0.500X0.250X0.100*%")

    with pytest.raises(UnsupportedFeatureError, match="contains a 0.1 hole"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_permissive_holed_aperture_skips_geometry_with_diagnostics(
    tmp_path: Path,
):
    path = _write(tmp_path, "%ADD10C,0.500X0.250*%")

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert any(
        diagnostic.code == "UNSUPPORTED_GERBER_APERTURE_HOLE"
        for diagnostic in result.diagnostics
    )
    assert any(
        diagnostic.code == "GERBER_APERTURE_GEOMETRY_SKIPPED"
        for diagnostic in result.diagnostics
    )


def test_zero_hole_diameter_is_invalid_not_silently_solid(tmp_path: Path):
    path = _write(tmp_path, "%ADD10C,0.500X0.000*%")

    with pytest.raises(ParseError, match="hole diameter must be positive"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_preflight_blocks_holed_standard_aperture(tmp_path: Path):
    path = _write(tmp_path, "%ADD10C,0.500X0.250*%")

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert report.strict_blockers
