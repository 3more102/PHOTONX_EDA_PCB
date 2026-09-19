from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.geometry_kernel import region_shape
from photonx_eda_pcb.gerber_image import (
    polygonize_regular_polygon_flash,
    polygonize_regular_polygon_track,
)
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "macro.gtl"
    path.write_text(text, encoding="utf-8")
    return path


def test_single_circle_macro_flash_is_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMROUND*1,1,$1,0,0*%\n"
        "%ADD10ROUND,0.800*%\n"
        "D10*\n"
        "X010000Y020000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu").parse(path)

    assert len(result.pads) == 1
    pad = result.pads[0]
    assert pad.shape == "C"
    assert pad.size_x == pytest.approx(0.8)
    assert pad.size_y == pytest.approx(0.8)


def test_single_circle_macro_can_be_used_for_linear_draw(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMTRACE*1,1,$1,0,0*%\n"
        "%ADD10TRACE,0.250*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu").parse(path)

    assert len(result.tracks) == 1
    assert result.tracks[0].width == pytest.approx(0.25)


def test_circle_macro_respects_active_inch_units(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOIN*%\n"
        "%AMROUND*1,1,$1,0,0*%\n"
        "%ADD10ROUND,0.010*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu").parse(path)

    assert result.pads[0].size_x == pytest.approx(0.254)


def test_centered_circle_macro_accepts_rotation_as_geometry_invariant(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMROUND*1,1,0.800,0,0,37*%\n"
        "%ADD10ROUND*%\n"
        "D10*\n"
        "X010000Y020000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    pad = result.pads[0]
    assert pad.shape == "C"
    assert pad.size_x == pytest.approx(0.8)
    assert pad.size_y == pytest.approx(0.8)


def test_centered_horizontal_vector_line_macro_flash_is_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMVLINE*20,1,$1,-1.0,0,1.0,0,0*%\n"
        "%ADD10VLINE,0.4*%\n"
        "D10*\n"
        "X010000Y020000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    pad = result.pads[0]
    assert pad.shape == "R"
    assert pad.center.x == pytest.approx(1.0)
    assert pad.center.y == pytest.approx(2.0)
    assert pad.size_x == pytest.approx(2.0)
    assert pad.size_y == pytest.approx(0.4)


def test_vector_line_macro_orthogonal_rotation_swaps_dimensions(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMVLINE*20,1,0.4,-1.0,0,1.0,0,90*%\n"
        "%ADD10VLINE*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    pad = result.pads[0]
    assert pad.shape == "R"
    assert pad.size_x == pytest.approx(0.4)
    assert pad.size_y == pytest.approx(2.0)


def test_legacy_code2_vector_line_alias_is_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMVLINE*2,1,0.2,-1,0,1,0,0*%\n"
        "%ADD10VLINE*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    pad = result.pads[0]
    assert pad.shape == "R"
    assert pad.size_x == pytest.approx(2.0)
    assert pad.size_y == pytest.approx(0.2)


def test_centered_vertical_vector_line_macro_respects_active_inch_units(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOIN*%\n"
        "%AMVLINE*20,1,0.010,0,-0.020,0,0.020,0*%\n"
        "%ADD10VLINE*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    pad = result.pads[0]
    assert pad.shape == "R"
    assert pad.size_x == pytest.approx(0.254)
    assert pad.size_y == pytest.approx(1.016)


@pytest.mark.parametrize(
    "macro_body",
    [
        "20,0,0.2,-1,0,1,0,0",
        "20,1,0,-1,0,1,0,0",
        "20,1,0.2,-1,0,1,0,30",
        "20,1,0.2,0,0,2,0,0",
        "20,1,0.2,-1,-1,1,1,0",
        "20,1,0.2,0,0,0,0,0",
    ],
)
def test_vector_line_macro_non_exact_cases_fail_closed(
    tmp_path: Path,
    macro_body: str,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        f"%AMVLINE*{macro_body}*%\n"
        "%ADD10VLINE*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_vector_line_rectangle_macro_draw_uses_exact_rectangular_sweep(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMVLINE*20,1,0.2,-1,0,1,0,0*%\n"
        "%ADD10VLINE*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks == []
    assert len(result.regions) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(0.6)
    assert any(
        evidence.kind == "gerber_track_polygonization"
        and "aperture_shape=R" in evidence.detail
        and "method=convex_sweep_exact" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_center_line_rectangle_macro_flash_is_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMBOX*21,1,$1,$2,0,0,0*%\n"
        "%ADD10BOX,1.0X2.0*%\n"
        "D10*\n"
        "X010000Y020000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    pad = result.pads[0]
    assert pad.shape == "R"
    assert pad.center.x == pytest.approx(1.0)
    assert pad.center.y == pytest.approx(2.0)
    assert pad.size_x == pytest.approx(1.0)
    assert pad.size_y == pytest.approx(2.0)


def test_center_line_rectangle_macro_orthogonal_rotation_swaps_dimensions(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMBOX*21,1,1.0,2.0,0,0,270*%\n"
        "%ADD10BOX*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    pad = result.pads[0]
    assert pad.shape == "R"
    assert pad.size_x == pytest.approx(2.0)
    assert pad.size_y == pytest.approx(1.0)


def test_center_line_rectangle_macro_draw_uses_exact_rectangular_sweep(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMBOX*21,1,1.0,2.0,0,0,0*%\n"
        "%ADD10BOX*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks == []
    assert len(result.regions) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(4.0)
    assert any(
        evidence.kind == "gerber_track_polygonization"
        and "aperture_shape=R" in evidence.detail
        and "method=convex_sweep_exact" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_center_line_rectangle_macro_respects_active_inch_units(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOIN*%\n"
        "%AMBOX*21,1,$1,$2,0,0,0*%\n"
        "%ADD10BOX,0.010X0.020*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu").parse(path)

    pad = result.pads[0]
    assert pad.size_x == pytest.approx(0.254)
    assert pad.size_y == pytest.approx(0.508)


@pytest.mark.parametrize(
    "macro_body",
    [
        "21,0,1.0,2.0,0,0,0",
        "21,1,1.0,2.0,0.1,0,0",
        "21,1,1.0,2.0,0,0.1,0",
        "21,1,1.0,2.0,0,0,30",
        "21,1,0,2.0,0,0,0",
        "21,1,1.0,0,0,0,0",
    ],
)
def test_center_line_rectangle_macro_non_exact_cases_fail_closed(
    tmp_path: Path,
    macro_body: str,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        f"%AMBOX*{macro_body}*%\n"
        "%ADD10BOX*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_lower_left_rectangle_macro_flash_is_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMLL*22,1,2.0,1.0,-1.0,-0.5,0*%\n"
        "%ADD10LL*%\n"
        "D10*\n"
        "X010000Y020000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    pad = result.pads[0]
    assert pad.shape == "R"
    assert pad.center.x == pytest.approx(1.0)
    assert pad.center.y == pytest.approx(2.0)
    assert pad.size_x == pytest.approx(2.0)
    assert pad.size_y == pytest.approx(1.0)


def test_lower_left_rectangle_macro_orthogonal_rotation_swaps_dimensions(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMLL*22,1,2.0,1.0,-1.0,-0.5,90*%\n"
        "%ADD10LL*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    pad = result.pads[0]
    assert pad.shape == "R"
    assert pad.size_x == pytest.approx(1.0)
    assert pad.size_y == pytest.approx(2.0)


def test_lower_left_rectangle_macro_respects_active_inch_units(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOIN*%\n"
        "%AMLL*22,1,0.040,0.010,-0.020,-0.005,180*%\n"
        "%ADD10LL*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    pad = result.pads[0]
    assert pad.size_x == pytest.approx(1.016)
    assert pad.size_y == pytest.approx(0.254)


@pytest.mark.parametrize(
    "macro_body",
    [
        "22,0,2.0,1.0,-1.0,-0.5,0",
        "22,1,0,1.0,0,-0.5,0",
        "22,1,2.0,0,-1.0,0,0",
        "22,1,2.0,1.0,0,-0.5,0",
        "22,1,2.0,1.0,-1.0,0,0",
        "22,1,2.0,1.0,-1.0,-0.5,45",
    ],
)
def test_lower_left_rectangle_macro_non_exact_cases_fail_closed(
    tmp_path: Path,
    macro_body: str,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        f"%AMLL*{macro_body}*%\n"
        "%ADD10LL*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_lower_left_rectangle_macro_composes_with_step_repeat(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMLL*22,1,2.0,1.0,-1.0,-0.5,90*%\n"
        "%ADD10LL*%\n"
        "D10*\n"
        "%SRX2Y1I3.0J0*%\n"
        "X000000Y000000D03*\n"
        "%SR*%\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 2
    assert [pad.center.x for pad in result.pads] == pytest.approx([0.0, 3.0])
    assert all(pad.size_x == pytest.approx(1.0) for pad in result.pads)
    assert all(pad.size_y == pytest.approx(2.0) for pad in result.pads)
    assert all(
        any(e.kind == "gerber_step_repeat" for e in pad.provenance.evidence)
        for pad in result.pads
    )


def test_lower_left_rectangle_macro_preflight_is_strict_ready(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMLL*22,1,2.0,1.0,-1.0,-0.5,270*%\n"
        "%ADD10LL*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_invalid_lower_left_rectangle_macro_preflight_blocks(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMLL*22,1,2.0,1.0,-1.0,-0.5,45*%\n"
        "%ADD10LL*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_APERTURE_MACRO" in blocker
        for blocker in report.strict_blockers
    )


def test_lower_left_rectangle_macro_draw_uses_exact_rectangular_sweep(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMLL*22,1,2.0,1.0,-1.0,-0.5,0*%\n"
        "%ADD10LL*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks == []
    assert len(result.regions) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(3.0)
    assert any(
        evidence.kind == "gerber_track_polygonization"
        and "aperture_shape=R" in evidence.detail
        and "method=convex_sweep_exact" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_permissive_invalid_lower_left_macro_skips_and_recovers(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMLL*22,1,2.0,1.0,0,0,45*%\n"
        "%ADD10LL*%\n"
        "%ADD11C,0.300*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "D11*\n"
        "X010000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert len(result.pads) == 1
    assert result.pads[0].shape == "C"
    assert any(
        d.code == "UNSUPPORTED_GERBER_APERTURE_MACRO"
        for d in result.diagnostics
    )
    assert any(
        d.code == "GERBER_APERTURE_GEOMETRY_SKIPPED"
        for d in result.diagnostics
    )


def test_multi_primitive_macro_remains_fail_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMCOMPLEX*21,1,1.0,2.0,0,0,0*1,1,0.2,0,0*%\n"
        "%ADD10COMPLEX*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_permissive_unsupported_macro_skips_geometry_and_continues(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMBOX*21,1,1.0,2.0,0,0,30*%\n"
        "%ADD10BOX*%\n"
        "%ADD11C,0.300*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "D11*\n"
        "X010000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert len(result.pads) == 1
    assert result.pads[0].size_x == pytest.approx(0.3)
    assert any(
        d.code == "UNSUPPORTED_GERBER_APERTURE_MACRO"
        for d in result.diagnostics
    )
    assert any(
        d.code == "GERBER_APERTURE_GEOMETRY_SKIPPED"
        for d in result.diagnostics
    )


def test_centered_polygon_macro_flash_is_reduced_exactly(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMPOLY*5,1,6,0,0,$1,30*%\n"
        "%ADD10POLY,2.0*%\n"
        "D10*\n"
        "X010000Y020000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_regular_polygon_flash(
        1.0,
        2.0,
        2.0,
        6,
        base_rotation_deg=30.0,
    ).geometry

    assert result.pads == []
    assert len(result.regions) == 1
    assert region_shape(result.regions[0]).symmetric_difference(
        expected
    ).area == pytest.approx(0.0, abs=1e-12)
    assert any(
        evidence.kind == "gerber_polygon_flash"
        and "vertices=6" in evidence.detail
        and "template_rotation_deg_ccw=30" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_polygon_macro_modifiers_and_inch_units_are_preserved(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOIN*%\n"
        "%AMPOLY*5,1,$1,0,0,$2,$3*%\n"
        "%ADD10POLY,5X0.040X-30*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    parser = GerberRS274XParser("F.Cu", strict=True)
    result = parser.parse(path)
    aperture = parser.apertures[10]

    assert aperture.shape == "P"
    assert aperture.polygon_vertices == 5
    assert aperture.polygon_rotation_deg == pytest.approx(330.0)
    assert aperture.x == pytest.approx(1.016)
    assert aperture.y == pytest.approx(1.016)
    assert len(result.regions) == 1


def test_polygon_macro_linear_draw_reuses_exact_polygon_sweep(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMPOLY*5,1,6,0,0,2,15*%\n"
        "%ADD10POLY*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X040000Y000000D01*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_regular_polygon_track(
        0.0,
        0.0,
        4.0,
        0.0,
        2.0,
        6,
        base_rotation_deg=15.0,
    ).geometry

    assert result.tracks == []
    assert len(result.regions) == 1
    assert region_shape(result.regions[0]).symmetric_difference(
        expected
    ).area == pytest.approx(0.0, abs=1e-12)
    assert any(
        evidence.kind == "gerber_polygon_track"
        and "method=convex_sweep_exact" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_polygon_macro_lpc_flash_composes_in_source_order(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10R,10X10*%\n"
        "%AMPOLY*5,1,6,0,0,4,0*%\n"
        "%ADD11POLY*%\n"
        "%LPD*%\n"
        "D10*\n"
        "X050000Y050000D03*\n"
        "%LPC*%\n"
        "D11*\n"
        "X050000Y050000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    clear_geometry = polygonize_regular_polygon_flash(
        5.0,
        5.0,
        4.0,
        6,
    ).geometry

    assert result.pads == []
    assert len(result.regions) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(
        100.0 - clear_geometry.area
    )
    assert any(
        evidence.kind == "gerber_polygon_flash"
        for evidence in result.regions[0].provenance.evidence
    )


@pytest.mark.parametrize(
    "macro_body",
    [
        "5,0,6,0,0,2,0",
        "5,1,2,0,0,2,0",
        "5,1,13,0,0,2,0",
        "5,1,5.5,0,0,2,0",
        "5,1,6,0.1,0,2,0",
        "5,1,6,0,0.1,2,0",
        "5,1,6,0,0,0,0",
    ],
)
def test_polygon_macro_non_exact_cases_fail_closed(
    tmp_path: Path,
    macro_body: str,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        f"%AMPOLY*{macro_body}*%\n"
        "%ADD10POLY*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_APERTURE_MACRO" in blocker
        for blocker in report.strict_blockers
    )


def test_polygon_macro_wrong_modifier_count_is_invalid(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMPOLY*5,1,6,0,0,2*%\n"
        "%ADD10POLY*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_GERBER_APERTURE_MACRO" in blocker
        for blocker in report.strict_blockers
    )


def test_polygon_macro_preflight_is_strict_ready(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMPOLY*5,1,8,0,0,3,22.5*%\n"
        "%ADD10POLY*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_permissive_invalid_polygon_macro_skips_and_recovers(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMPOLY*5,1,6,1,0,2,0*%\n"
        "%ADD10POLY*%\n"
        "%ADD11C,0.300*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "D11*\n"
        "X010000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert len(result.pads) == 1
    assert result.pads[0].shape == "C"
    assert any(
        d.code == "UNSUPPORTED_GERBER_APERTURE_MACRO"
        for d in result.diagnostics
    )
    assert any(
        d.code == "GERBER_APERTURE_GEOMETRY_SKIPPED"
        for d in result.diagnostics
    )
