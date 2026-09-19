from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.geometry_kernel import region_shape
from photonx_eda_pcb.gerber_image import polygonize_holed_flash
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


@pytest.mark.parametrize(
    ("definition", "shape", "x_mm", "y_mm", "hole_mm"),
    [
        ("%ADD10C,0.500X0.250*%", "C", 0.5, 0.5, 0.25),
        ("%ADD10R,0.500X0.250X0.100*%", "R", 0.5, 0.25, 0.1),
        ("%ADD10O,0.500X0.250X0.100*%", "O", 0.5, 0.25, 0.1),
    ],
)
def test_standard_holed_flash_materializes_transparent_region(
    tmp_path: Path,
    definition: str,
    shape: str,
    x_mm: float,
    y_mm: float,
    hole_mm: float,
):
    path = _write(tmp_path, definition)

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_holed_flash(
        1.0,
        2.0,
        x_mm,
        y_mm,
        shape,
        hole_mm,
    ).geometry

    assert result.pads == []
    assert len(result.regions) == 1
    region = result.regions[0]
    actual = region_shape(region)
    assert len(region.holes) == 1
    assert actual.symmetric_difference(expected).area == pytest.approx(
        0.0,
        abs=1e-12,
    )
    assert any(
        evidence.kind == "gerber_aperture_hole"
        and f"outer_shape={shape}" in evidence.detail
        and f"hole_diameter_mm={hole_mm:.12g}" in evidence.detail
        and "hole_semantics=transparent" in evidence.detail
        for evidence in region.provenance.evidence
    )


def test_valid_holed_aperture_is_strict_preflight_ready(tmp_path: Path):
    path = _write(tmp_path, "%ADD10C,0.500X0.250*%")

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_zero_hole_diameter_is_invalid_not_silently_solid(tmp_path: Path):
    path = _write(tmp_path, "%ADD10C,0.500X0.000*%")

    with pytest.raises(ParseError, match="hole diameter must be positive"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


@pytest.mark.parametrize(
    "definition",
    [
        "%ADD10C,0.500X0.500*%",
        "%ADD10R,0.500X0.250X0.250*%",
        "%ADD10O,0.500X0.250X0.300*%",
    ],
)
def test_hole_must_strictly_fit_outer_aperture(
    tmp_path: Path,
    definition: str,
):
    path = _write(tmp_path, definition)

    with pytest.raises(ParseError, match="must strictly fit"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_GERBER_APERTURE_HOLE_FIT" in blocker
        for blocker in report.strict_blockers
    )


def test_permissive_nonfitting_hole_skips_geometry_with_diagnostics(
    tmp_path: Path,
):
    path = _write(tmp_path, "%ADD10R,0.500X0.250X0.250*%")

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert result.regions == []
    assert any(
        diagnostic.code == "INVALID_GERBER_APERTURE_HOLE_FIT"
        for diagnostic in result.diagnostics
    )
    assert any(
        diagnostic.code == "GERBER_APERTURE_GEOMETRY_SKIPPED"
        for diagnostic in result.diagnostics
    )


def test_holed_linear_draw_remains_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,0.500X0.250*%",
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="holed aperture"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_APERTURE_HOLE_DRAW" in blocker
        for blocker in report.strict_blockers
    )


def test_permissive_holed_draw_advances_current_point_and_recovers(
    tmp_path: Path,
):
    path = tmp_path / "recover.gtl"
    path.write_text(
        HEADER
        + "%ADD10C,0.500X0.250*%\n"
        + "%ADD11C,0.200*%\n"
        + "D10*\n"
        + "X000000Y000000D02*\n"
        + "X010000Y000000D01*\n"
        + "D11*\n"
        + "X020000Y000000D01*\n"
        + "M02*\n",
        encoding="utf-8",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert len(result.tracks) == 1
    track = result.tracks[0]
    assert (track.start.x, track.start.y) == pytest.approx((1.0, 0.0))
    assert (track.end.x, track.end.y) == pytest.approx((2.0, 0.0))
    assert any(
        diagnostic.code == "UNSUPPORTED_GERBER_APERTURE_HOLE_DRAW"
        for diagnostic in result.diagnostics
    )


def test_holed_arc_draw_remains_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,0.500X0.250*%",
        "G75*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I-010000J000000D01*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="holed aperture"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_holed_flash_scaling_scales_outer_and_hole(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10R,0.500X0.250X0.100*%",
        "%LS2*%\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_holed_flash(
        1.0,
        2.0,
        1.0,
        0.5,
        "R",
        0.2,
    ).geometry

    actual = region_shape(result.regions[0])
    assert actual.symmetric_difference(expected).area == pytest.approx(
        0.0,
        abs=1e-12,
    )
    assert any(
        evidence.kind == "gerber_aperture_hole"
        and "hole_diameter_mm=0.2" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_holed_flash_arbitrary_rotation_and_ir_compose(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10O,0.600X0.300X0.100*%",
        "%LR30*%\n"
        "%IR90*%\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_holed_flash(
        -2.0,
        1.0,
        0.6,
        0.3,
        "O",
        0.1,
        rotation_deg=120.0,
    ).geometry

    actual = region_shape(result.regions[0])
    assert actual.symmetric_difference(expected).area == pytest.approx(
        0.0,
        abs=1e-12,
    )
    assert any(
        evidence.kind == "gerber_aperture_hole"
        and "rotation_deg_ccw=120" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_holed_dark_flash_does_not_clear_preexisting_material(tmp_path: Path):
    path = tmp_path / "transparent_hole.gtl"
    path.write_text(
        HEADER
        + "%ADD10R,2X2*%\n"
        + "%ADD11R,4X4X2*%\n"
        + "%LPD*%\n"
        + "D10*\n"
        + "X050000Y050000D03*\n"
        + "D11*\n"
        + "X050000Y050000D03*\n"
        + "%LPC*%\n"
        + "%LPD*%\n"
        + "M02*\n",
        encoding="utf-8",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.pads == []
    assert len(result.regions) == 1
    shape = region_shape(result.regions[0])
    # The first 2x2 flash remains visible through the transparent 2 mm hole.
    assert shape.area == pytest.approx(16.0)
    assert len(result.regions[0].holes) == 0


def test_clear_holed_flash_only_clears_annulus_not_center(tmp_path: Path):
    path = tmp_path / "clear_transparent_hole.gtl"
    path.write_text(
        HEADER
        + "%ADD10R,10X10*%\n"
        + "%ADD11R,4X4X2*%\n"
        + "%LPD*%\n"
        + "D10*\n"
        + "X050000Y050000D03*\n"
        + "%LPC*%\n"
        + "D11*\n"
        + "X050000Y050000D03*\n"
        + "M02*\n",
        encoding="utf-8",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    clear_shape = polygonize_holed_flash(
        5.0,
        5.0,
        4.0,
        4.0,
        "R",
        2.0,
    ).geometry

    assert result.pads == []
    assert len(result.regions) == 2
    total_area = sum(region_shape(region).area for region in result.regions)
    assert total_area == pytest.approx(100.0 - clear_shape.area)


def test_zero_circle_flash_is_legal_no_image_object(tmp_path: Path):
    path = _write(tmp_path, "%ADD10C,0.000*%")

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.pads == []
    assert result.tracks == []
    assert result.regions == []
    assert result.outline == []
    assert any(
        diagnostic.code == "GERBER_ZERO_SIZE_OBJECT_NO_IMAGE"
        and "operation=D03" in diagnostic.message
        for diagnostic in result.diagnostics
    )


def test_zero_circle_linear_draw_updates_current_without_emitting_geometry(
    tmp_path: Path,
):
    path = tmp_path / "zero_draw.gtl"
    path.write_text(
        HEADER
        + "%ADD10C,0.000*%\n"
        + "%ADD11C,0.200*%\n"
        + "D10*\n"
        + "X000000Y000000D02*\n"
        + "X010000Y000000D01*\n"
        + "D11*\n"
        + "X020000Y000000D01*\n"
        + "M02*\n",
        encoding="utf-8",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 1
    track = result.tracks[0]
    assert (track.start.x, track.start.y) == pytest.approx((1.0, 0.0))
    assert (track.end.x, track.end.y) == pytest.approx((2.0, 0.0))
    assert any(
        diagnostic.code == "GERBER_ZERO_SIZE_OBJECT_NO_IMAGE"
        and "operation=D01" in diagnostic.message
        for diagnostic in result.diagnostics
    )


def test_zero_circle_arc_validates_path_but_emits_no_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,0.000*%",
        "G75*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I-010000J000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks == []
    assert result.regions == []
    assert any(
        diagnostic.code == "GERBER_ZERO_SIZE_OBJECT_NO_IMAGE"
        for diagnostic in result.diagnostics
    )


def test_zero_circle_on_edge_cuts_emits_no_outline(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,0.000*%",
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("Edge.Cuts", strict=True).parse(path)

    assert result.outline == []
    assert result.tracks == []
    assert any(
        diagnostic.code == "GERBER_ZERO_SIZE_OBJECT_NO_IMAGE"
        for diagnostic in result.diagnostics
    )


def test_preflight_accepts_zero_circle_diameter(tmp_path: Path):
    path = _write(tmp_path, "%ADD10C,0.000*%")

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_zero_circle_cannot_have_positive_hole(tmp_path: Path):
    path = _write(tmp_path, "%ADD10C,0.000X0.100*%")

    with pytest.raises(ParseError, match="must strictly fit"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)
