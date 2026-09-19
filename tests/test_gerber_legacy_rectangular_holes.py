from pathlib import Path

import pytest
from shapely.geometry import Polygon

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.geometry_kernel import region_shape
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


HEADER = """%FSLAX24Y24*%
%MOMM*%
"""


def _write(
    tmp_path: Path,
    aperture: str,
    body: str = "X010000Y020000D03*\n",
) -> Path:
    path = tmp_path / "legacy_rect_hole.gtl"
    path.write_text(
        HEADER + aperture + "\nD10*\n" + body + "M02*\n",
        encoding="utf-8",
    )
    return path


def _hole_shape(result) -> Polygon:
    assert result.pads == []
    assert len(result.regions) == 1
    region = result.regions[0]
    assert len(region.holes) == 1
    return Polygon([(point.x, point.y) for point in region.holes[0]])


@pytest.mark.parametrize(
    "definition",
    [
        "%ADD10C,4X1X0.5*%",
        "%ADD10R,4X2X1X0.5*%",
        "%ADD10O,4X2X1X0.5*%",
    ],
)
def test_legacy_rectangular_hole_materializes_exact_transparent_hole(
    tmp_path: Path,
    definition: str,
):
    result = GerberRS274XParser("F.Cu", strict=True).parse(
        _write(tmp_path, definition)
    )

    hole = _hole_shape(result)
    assert hole.area == pytest.approx(0.5)
    assert hole.bounds == pytest.approx((0.5, 1.75, 1.5, 2.25))
    assert any(
        evidence.kind == "gerber_aperture_hole"
        and "hole_shape=rectangular" in evidence.detail
        and "hole_size_x_mm=1" in evidence.detail
        and "hole_size_y_mm=0.5" in evidence.detail
        and "hole_semantics=transparent" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_polygon_template_rotation_does_not_rotate_legacy_rectangular_hole(
    tmp_path: Path,
):
    result = GerberRS274XParser("F.Cu", strict=True).parse(
        _write(tmp_path, "%ADD10P,4X6X30X1X0.5*%")
    )

    hole = _hole_shape(result)
    assert hole.area == pytest.approx(0.5)
    assert hole.bounds == pytest.approx((0.5, 1.75, 1.5, 2.25))
    assert any(
        evidence.kind == "gerber_polygon_flash"
        and "template_rotation_deg_ccw=30" in evidence.detail
        and "rect_hole_x_mm=1" in evidence.detail
        and "rect_hole_y_mm=0.5" in evidence.detail
        and "rect_hole_rotation_deg_ccw=0" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_lr_rotates_outer_aperture_but_not_legacy_rectangular_hole(
    tmp_path: Path,
):
    result = GerberRS274XParser("F.Cu", strict=True).parse(
        _write(
            tmp_path,
            "%ADD10R,4X2X1.5X0.5*%",
            "%LR90*%\nX010000Y020000D03*\n",
        )
    )

    hole = _hole_shape(result)
    assert hole.bounds == pytest.approx((0.25, 1.75, 1.75, 2.25))


def test_whole_image_rotation_rotates_legacy_rectangular_hole(
    tmp_path: Path,
):
    result = GerberRS274XParser("F.Cu", strict=True).parse(
        _write(
            tmp_path,
            "%ADD10R,4X2X1.5X0.5*%",
            "%IR90*%\nX010000Y020000D03*\n",
        )
    )

    hole = _hole_shape(result)
    assert hole.area == pytest.approx(0.75)
    assert hole.bounds == pytest.approx((-2.25, 0.25, -1.75, 1.75))


def test_ls_scales_legacy_rectangular_hole_dimensions(tmp_path: Path):
    result = GerberRS274XParser("F.Cu", strict=True).parse(
        _write(
            tmp_path,
            "%ADD10R,4X2X1X0.5*%",
            "%LS2*%\nX010000Y020000D03*\n",
        )
    )

    hole = _hole_shape(result)
    assert hole.area == pytest.approx(2.0)
    assert hole.bounds == pytest.approx((0.0, 1.5, 2.0, 2.5))


def test_nonfitting_legacy_rectangular_hole_is_strict_blocker(tmp_path: Path):
    path = _write(tmp_path, "%ADD10R,2X1X2X0.5*%")

    with pytest.raises(ParseError, match="must strictly fit"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_GERBER_APERTURE_HOLE_FIT" in blocker
        for blocker in report.strict_blockers
    )


def test_legacy_rectangular_holed_draw_remains_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10C,4X1X0.5*%",
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="holed aperture"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_valid_legacy_rectangular_hole_is_preflight_ready(tmp_path: Path):
    report = preflight(_write(tmp_path, "%ADD10R,4X2X1X0.5*%"))

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers
