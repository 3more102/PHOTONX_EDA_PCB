from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.geometry_kernel import region_shape
from photonx_eda_pcb.gerber_image import (
    polygonize_regular_polygon_flash,
    polygonize_regular_polygon_track,
)
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


HEADER = """%FSLAX24Y24*%
%MOMM*%
"""


def _write(tmp_path: Path, aperture: str, body: str = "X010000Y020000D03*\n") -> Path:
    path = tmp_path / "polygon.gtl"
    path.write_text(
        HEADER + aperture + "\nD10*\n" + body + "M02*\n",
        encoding="utf-8",
    )
    return path


def test_standard_polygon_hex_flash_materializes_exact_region(tmp_path: Path):
    path = _write(tmp_path, "%ADD10P,0.040X6*%")

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_regular_polygon_flash(
        1.0,
        2.0,
        0.040,
        6,
    ).geometry

    assert result.pads == []
    assert len(result.regions) == 1
    actual = region_shape(result.regions[0])
    assert actual.symmetric_difference(expected).area == pytest.approx(
        0.0,
        abs=1e-15,
    )
    assert any(
        evidence.kind == "gerber_polygon_flash"
        and "vertices=6" in evidence.detail
        and "approximated=false" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_polygon_template_rotation_is_counterclockwise(tmp_path: Path):
    path = _write(tmp_path, "%ADD10P,4X5X30*%")

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_regular_polygon_flash(
        1.0,
        2.0,
        4.0,
        5,
        base_rotation_deg=30.0,
    ).geometry

    actual = region_shape(result.regions[0])
    assert actual.symmetric_difference(expected).area == pytest.approx(
        0.0,
        abs=1e-12,
    )


def test_polygon_negative_template_rotation_is_accepted(tmp_path: Path):
    path = _write(tmp_path, "%ADD10P,4X5X-30*%")

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_regular_polygon_flash(
        1.0,
        2.0,
        4.0,
        5,
        base_rotation_deg=-30.0,
    ).geometry

    assert region_shape(result.regions[0]).symmetric_difference(
        expected
    ).area == pytest.approx(0.0, abs=1e-12)


def test_polygon_round_hole_is_transparent_region_hole(tmp_path: Path):
    path = _write(tmp_path, "%ADD10P,4X6X0X1*%")

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_regular_polygon_flash(
        1.0,
        2.0,
        4.0,
        6,
        hole_diameter=1.0,
    )

    assert len(result.regions) == 1
    region = result.regions[0]
    assert len(region.holes) == 1
    assert region_shape(region).symmetric_difference(
        expected.geometry
    ).area == pytest.approx(0.0, abs=1e-12)
    assert any(
        evidence.kind == "gerber_polygon_flash"
        and "hole_diameter_mm=1" in evidence.detail
        and "approximated=true" in evidence.detail
        and "max_chord_error_mm=0.005" in evidence.detail
        for evidence in region.provenance.evidence
    )


def test_polygon_lm_lr_ls_and_ir_compose_in_spec_order(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10P,2X5X17*%",
        "%LMX*%\n"
        "%LR30*%\n"
        "%LS2*%\n"
        "%IR90*%\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_regular_polygon_flash(
        -2.0,
        1.0,
        4.0,
        5,
        base_rotation_deg=17.0,
        mirror="X",
        object_rotation_deg=120.0,
    ).geometry

    actual = region_shape(result.regions[0])
    assert actual.symmetric_difference(expected).area == pytest.approx(
        0.0,
        abs=1e-12,
    )
    kinds = {e.kind for e in result.regions[0].provenance.evidence}
    assert {
        "gerber_aperture_mirror",
        "gerber_aperture_rotation",
        "gerber_aperture_scale",
        "gerber_polygon_flash",
    }.issubset(kinds)


@pytest.mark.parametrize(
    ("definition", "code"),
    [
        ("%ADD10P,4X2*%", "INVALID_GERBER_POLYGON_VERTEX_COUNT"),
        ("%ADD10P,4X13*%", "INVALID_GERBER_POLYGON_VERTEX_COUNT"),
        ("%ADD10P,4X5.5*%", "INVALID_GERBER_POLYGON_VERTEX_COUNT"),
        ("%ADD10P,0X6*%", "INVALID_GERBER_STANDARD_APERTURE_SIZE"),
        ("%ADD10P,4X4X0X3*%", "INVALID_GERBER_APERTURE_HOLE_FIT"),
    ],
)
def test_invalid_polygon_apertures_fail_strict_and_preflight(
    tmp_path: Path,
    definition: str,
    code: str,
):
    path = _write(tmp_path, definition)

    with pytest.raises(ParseError):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction
    assert any(code in blocker for blocker in report.strict_blockers)


def test_polygon_d01_draw_materializes_exact_convex_sweep(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10P,1X6*%",
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_regular_polygon_track(
        0.0,
        0.0,
        1.0,
        0.0,
        1.0,
        6,
    ).geometry

    assert result.tracks == []
    assert len(result.regions) == 1
    actual = region_shape(result.regions[0])
    assert actual.symmetric_difference(expected).area == pytest.approx(
        0.0,
        abs=1e-12,
    )
    assert any(
        evidence.kind == "gerber_polygon_track"
        and "method=convex_sweep_exact" in evidence.detail
        and "approximated=false" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )

    report = preflight(path)
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_polygon_draw_advances_current_and_recovers_to_circular_track(tmp_path: Path):
    path = tmp_path / "polygon_recover.gtl"
    path.write_text(
        HEADER
        + "%ADD10P,1X6*%\n"
        + "%ADD11C,0.2*%\n"
        + "D10*\n"
        + "X000000Y000000D02*\n"
        + "X010000Y000000D01*\n"
        + "D11*\n"
        + "X020000Y000000D01*\n"
        + "M02*\n",
        encoding="utf-8",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    assert len(result.tracks) == 1
    assert (result.tracks[0].start.x, result.tracks[0].start.y) == pytest.approx(
        (1.0, 0.0)
    )
    assert (result.tracks[0].end.x, result.tracks[0].end.y) == pytest.approx(
        (2.0, 0.0)
    )


def test_holed_polygon_d01_remains_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10P,2X6X0X0.5*%",
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="holed P aperture"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_APERTURE_HOLE_DRAW" in blocker
        for blocker in report.strict_blockers
    )


def test_polygon_d01_transforms_compose_exactly(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10P,2X5X17*%",
        "%LMY*%\n"
        "%LR30*%\n"
        "%LS1.5*%\n"
        "%IR90*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_regular_polygon_track(
        0.0,
        0.0,
        0.0,
        1.0,
        3.0,
        5,
        base_rotation_deg=17.0,
        mirror="Y",
        object_rotation_deg=120.0,
    ).geometry

    actual = region_shape(result.regions[0])
    assert actual.symmetric_difference(expected).area == pytest.approx(
        0.0,
        abs=1e-12,
    )
    kinds = {e.kind for e in result.regions[0].provenance.evidence}
    assert {
        "gerber_aperture_mirror",
        "gerber_aperture_rotation",
        "gerber_aperture_scale",
        "gerber_polygon_track",
    }.issubset(kinds)


def test_polygon_flash_step_repeat_materializes_each_instance(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ADD10P,2X6X15*%",
        "%SRX2Y1I5J0*%\n"
        "X010000Y020000D03*\n"
        "%SR*%\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 2
    centers = [
        region_shape(region).centroid.x
        for region in result.regions
    ]
    assert sorted(centers) == pytest.approx([1.0, 6.0])


def test_lpc_holed_polygon_flash_clears_polygon_ring_not_center(tmp_path: Path):
    path = tmp_path / "polygon_lpc.gtl"
    path.write_text(
        HEADER
        + "%ADD10R,10X10*%\n"
        + "%ADD11P,4X6X0X1*%\n"
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
    clear_geometry = polygonize_regular_polygon_flash(
        5.0,
        5.0,
        4.0,
        6,
        hole_diameter=1.0,
    ).geometry

    assert result.pads == []
    total_area = sum(region_shape(region).area for region in result.regions)
    assert total_area == pytest.approx(100.0 - clear_geometry.area)

    report = preflight(path)
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_lpc_polygon_draw_subtracts_exact_sweep(tmp_path: Path):
    path = tmp_path / "polygon_draw_lpc.gtl"
    path.write_text(
        HEADER
        + "%ADD10R,10X10*%\n"
        + "%ADD11P,2X6X15*%\n"
        + "%LPD*%\n"
        + "D10*\n"
        + "X050000Y050000D03*\n"
        + "%LPC*%\n"
        + "D11*\n"
        + "X030000Y050000D02*\n"
        + "X070000Y050000D01*\n"
        + "M02*\n",
        encoding="utf-8",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    clear_geometry = polygonize_regular_polygon_track(
        3.0,
        5.0,
        7.0,
        5.0,
        2.0,
        6,
        base_rotation_deg=15.0,
    ).geometry

    assert result.pads == []
    assert len(result.regions) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(
        100.0 - clear_geometry.area
    )
    assert any(
        evidence.kind == "gerber_polygon_track"
        for evidence in result.regions[0].provenance.evidence
    )

    report = preflight(path)
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers
