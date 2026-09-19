from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.geometry_kernel import region_shape
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


def test_circle_hole_modifier_materializes_explicit_copper_hole(tmp_path: Path):
    path = _write(tmp_path, "%ADD10C,0.500X0.250*%")

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.pads == []
    assert len(result.regions) == 1
    region = result.regions[0]
    assert len(region.holes) == 1
    assert region_shape(region).area > 0.0
    assert any(
        evidence.kind == "gerber_aperture_hole"
        and "hole_diameter_mm=0.25" in evidence.detail
        and "image_clearance_not_physical_drill" in evidence.detail
        for evidence in region.provenance.evidence
    )


def test_rectangle_hole_modifier_materializes_explicit_copper_hole(tmp_path: Path):
    path = _write(tmp_path, "%ADD10R,0.500X0.250X0.100*%")

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.pads == []
    assert len(result.regions) == 1
    assert len(result.regions[0].holes) == 1
    assert region_shape(result.regions[0]).area > 0.0


def test_permissive_holed_flash_preserves_geometry_without_unsupported_diagnostic(
    tmp_path: Path,
):
    path = _write(tmp_path, "%ADD10C,0.500X0.250*%")

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert len(result.regions) == 1
    assert not any(
        diagnostic.code == "UNSUPPORTED_GERBER_APERTURE_HOLE"
        for diagnostic in result.diagnostics
    )


def test_zero_hole_diameter_is_invalid_not_silently_solid(tmp_path: Path):
    path = _write(tmp_path, "%ADD10C,0.500X0.000*%")

    with pytest.raises(ParseError, match="hole diameter must be positive"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_preflight_accepts_holed_standard_flash_aperture(tmp_path: Path):
    path = _write(tmp_path, "%ADD10C,0.500X0.250*%")

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_holed_aperture_d01_draw_remains_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,0.500X0.250*%",
        body="X000000Y000000D02*\nX010000Y000000D01*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="D01 draws with holed apertures"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_holed_aperture_g75_arc_draw_remains_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,0.500X0.250*%",
        body=(
            "G75*\n"
            "X010000Y000000D02*\n"
            "G03X000000Y010000I-010000J000000D01*\n"
        ),
    )

    with pytest.raises(UnsupportedFeatureError, match="G02/G03 draws with holed apertures"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_zero_circle_diameter_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(tmp_path, "%ADD10C,0.000*%")

    with pytest.raises(ParseError, match="diameter must be positive"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_zero_circle_diameter_skips_permissive_geometry(tmp_path: Path):
    path = _write(tmp_path, "%ADD10C,0.000*%")

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert any(
        diagnostic.code == "INVALID_GERBER_STANDARD_APERTURE_SIZE"
        for diagnostic in result.diagnostics
    )
    assert any(
        diagnostic.code == "GERBER_APERTURE_GEOMETRY_SKIPPED"
        for diagnostic in result.diagnostics
    )


def test_preflight_blocks_zero_circle_diameter(tmp_path: Path):
    path = _write(tmp_path, "%ADD10C,0.000*%")

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_GERBER_STANDARD_APERTURE_SIZE" in blocker
        for blocker in report.strict_blockers
    )
