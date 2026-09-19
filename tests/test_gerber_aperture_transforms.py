from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.geometry_kernel import region_shape
from photonx_eda_pcb.gerber_image import polygonize_rotated_flash
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


BASE = """%FSLAX24Y24*%
%MOMM*%
%ADD10R,0.600X0.300*%
D10*
"""


def _write(tmp_path: Path, body: str, name: str = "top.gtl") -> Path:
    path = tmp_path / name
    path.write_text(BASE + body + "M02*\n", encoding="utf-8")
    return path


@pytest.mark.parametrize("command", ["%LMN*%", "%LR0*%", "%LR360*%", "%LS1*%"])
def test_identity_aperture_transforms_keep_supported_geometry(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    pad = result.pads[0]
    assert pad.size_x == pytest.approx(0.6)
    assert pad.size_y == pytest.approx(0.3)


@pytest.mark.parametrize("command", ["%LMX*%", "%LMY*%", "%LMXY*%"])
def test_mirroring_is_exact_for_centered_symmetric_rectangle(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    pad = result.pads[0]
    assert pad.size_x == pytest.approx(0.6)
    assert pad.size_y == pytest.approx(0.3)
    assert any(
        evidence.kind == "gerber_aperture_mirror"
        for evidence in pad.provenance.evidence
    )


@pytest.mark.parametrize(
    ("rotation", "expected"),
    [
        (90, (0.3, 0.6)),
        (180, (0.6, 0.3)),
        (270, (0.3, 0.6)),
        (450, (0.3, 0.6)),
    ],
)
def test_orthogonal_rectangle_rotation_is_exact(
    tmp_path: Path,
    rotation: int,
    expected: tuple[float, float],
):
    path = _write(
        tmp_path,
        f"%LR{rotation}*%\n"
        "X010000Y020000D03*\n",
    )

    pad = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    assert (pad.size_x, pad.size_y) == pytest.approx(expected)
    assert any(
        evidence.kind == "gerber_aperture_rotation"
        for evidence in pad.provenance.evidence
    )


def test_aperture_scaling_scales_flash_not_center(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LS2*%\n"
        "X010000Y020000D03*\n",
    )

    pad = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    assert (pad.center.x, pad.center.y) == pytest.approx((1.0, 2.0))
    assert (pad.size_x, pad.size_y) == pytest.approx((1.2, 0.6))
    assert any(
        evidence.kind == "gerber_aperture_scale"
        and "scale=2" in evidence.detail
        for evidence in pad.provenance.evidence
    )


def test_combined_lm_lr_ls_applies_to_original_aperture(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LMX*%\n"
        "%LR90*%\n"
        "%LS2*%\n"
        "X010000Y020000D03*\n",
    )

    pad = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    assert (pad.size_x, pad.size_y) == pytest.approx((0.6, 1.2))
    kinds = {e.kind for e in pad.provenance.evidence}
    assert {
        "gerber_aperture_mirror",
        "gerber_aperture_rotation",
        "gerber_aperture_scale",
    }.issubset(kinds)


def test_modal_scaling_replaces_previous_value_instead_of_accumulating(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%LS2*%\n"
        "X010000Y020000D03*\n"
        "%LS0.5*%\n"
        "X020000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 2
    assert (result.pads[0].size_x, result.pads[0].size_y) == pytest.approx(
        (1.2, 0.6)
    )
    assert (result.pads[1].size_x, result.pads[1].size_y) == pytest.approx(
        (0.3, 0.15)
    )


def test_modal_rotation_reset_restores_original_rectangle_orientation(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%LR90*%\n"
        "X010000Y020000D03*\n"
        "%LR0*%\n"
        "X020000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert (result.pads[0].size_x, result.pads[0].size_y) == pytest.approx(
        (0.3, 0.6)
    )
    assert (result.pads[1].size_x, result.pads[1].size_y) == pytest.approx(
        (0.6, 0.3)
    )


def test_nonorthogonal_rectangle_rotation_materializes_exact_region(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%LR45*%\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_rotated_flash(
        1.0,
        2.0,
        0.6,
        0.3,
        "R",
        rotation_deg=45.0,
    ).geometry

    assert result.pads == []
    assert len(result.regions) == 1
    actual = region_shape(result.regions[0])
    assert actual.symmetric_difference(expected).area == pytest.approx(
        0.0,
        abs=1e-12,
    )
    assert any(
        evidence.kind == "gerber_flash_polygonization"
        and "method=rotated_polygon_exact" in evidence.detail
        and "rotation_deg_ccw=45" in evidence.detail
        and "approximated=false" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_nonorthogonal_rectangle_rotation_preserves_other_file_geometry(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "X000000Y000000D03*\n"
        "%LR45*%\n"
        "X010000Y020000D03*\n"
        "%LR0*%\n"
        "X020000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert len(result.pads) == 2
    assert len(result.regions) == 1
    assert result.tracks == []
    assert result.outline == []
    assert not any(
        diagnostic.code == "UNSUPPORTED_GERBER_APERTURE_TRANSFORM"
        for diagnostic in result.diagnostics
    )


def test_arbitrary_rotation_is_geometry_invariant_for_circle_flash(tmp_path: Path):
    path = tmp_path / "circle_flash.gtl"
    path.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.400*%\n"
        "D10*\n"
        "%LR37.5*%\n"
        "%LMXY*%\n"
        "X010000Y020000D03*\n"
        "M02*\n",
        encoding="utf-8",
    )

    pad = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    assert (pad.size_x, pad.size_y) == pytest.approx((0.4, 0.4))
    kinds = {e.kind for e in pad.provenance.evidence}
    assert "gerber_aperture_rotation" in kinds
    assert "gerber_aperture_mirror" in kinds


def test_aperture_scaling_scales_circular_draw_width(tmp_path: Path):
    path = tmp_path / "circle_draw.gtl"
    path.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "%LS2.5*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "M02*\n",
        encoding="utf-8",
    )

    track = GerberRS274XParser("F.Cu", strict=True).parse(path).tracks[0]

    assert track.width == pytest.approx(0.5)
    assert any(
        e.kind == "gerber_aperture_scale" for e in track.provenance.evidence
    )


def test_aperture_scaling_scales_circular_arc_width_not_path_radius(tmp_path: Path):
    path = tmp_path / "circle_arc.gtl"
    path.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "%LS3*%\n"
        "%LR33*%\n"
        "G75*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I-010000J000000D01*\n"
        "M02*\n",
        encoding="utf-8",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks
    assert all(track.width == pytest.approx(0.6) for track in result.tracks)
    assert all(
        any(
            e.kind == "gerber_arc_tessellation"
            and "radius_mm=1" in e.detail
            for e in track.provenance.evidence
        )
        for track in result.tracks
    )


def test_aperture_rotation_composes_with_whole_image_rotation(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LR90*%\n"
        "%LS2*%\n"
        "%IR90*%\n"
        "X010000Y020000D03*\n",
    )

    pad = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    # LR90 swaps 1.2x0.6 -> 0.6x1.2; IR90 rotates the whole image -> 1.2x0.6.
    assert (pad.size_x, pad.size_y) == pytest.approx((1.2, 0.6))


def test_exact_reduced_macro_composes_with_aperture_transform(tmp_path: Path):
    path = tmp_path / "macro_transform.gtl"
    path.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMBOX*21,1,1.0,2.0,0,0,0*%\n"
        "%ADD10BOX*%\n"
        "D10*\n"
        "%LR90*%\n"
        "%LS2*%\n"
        "X000000Y000000D03*\n"
        "M02*\n",
        encoding="utf-8",
    )

    pad = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    assert pad.shape == "R"
    assert (pad.size_x, pad.size_y) == pytest.approx((4.0, 2.0))


@pytest.mark.parametrize(
    "command",
    [
        "%LS0*%\n",
        "%LS-1*%\n",
        "%LS999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999*%\n",
    ],
)
def test_invalid_aperture_scaling_is_rejected(tmp_path: Path, command: str):
    path = _write(
        tmp_path,
        command
        + "X010000Y020000D03*\n",
    )

    with pytest.raises(ParseError):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_non_finite_rotation_is_rejected(tmp_path: Path):
    huge = "9" * 400
    path = _write(
        tmp_path,
        f"%LR{huge}*%\n"
        "X010000Y020000D03*\n",
    )

    with pytest.raises(ParseError, match="rotation must be finite"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_malformed_aperture_transform_is_invalid_and_suppressed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LRABC*%\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert any(
        diagnostic.code == "INVALID_GERBER_APERTURE_TRANSFORM"
        for diagnostic in result.diagnostics
    )


def test_preflight_accepts_supported_nonidentity_aperture_transforms(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%LMY*%\n"
        "%LR90*%\n"
        "%LS2*%\n"
        "X010000Y020000D03*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_preflight_accepts_nonorthogonal_rectangle_rotation(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LR45*%\n"
        "X010000Y020000D03*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_aperture_transform_changes_stable_id_on_same_source_path(tmp_path: Path):
    path = _write(
        tmp_path,
        "X010000Y020000D03*\n",
        name="same_transform_source.gtl",
    )
    plain = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    path.write_text(
        BASE
        + "%LS2*%\n"
        + "X010000Y020000D03*\n"
        + "M02*\n",
        encoding="utf-8",
    )
    scaled = GerberRS274XParser("F.Cu", strict=True).parse(path).pads[0]

    assert plain.id != scaled.id


def test_nonorthogonal_obround_flash_is_materialized_with_bounded_curves(
    tmp_path: Path,
):
    path = tmp_path / "obround_lr.gtl"
    path.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10O,0.600X0.300*%\n"
        "D10*\n"
        "%LR30*%\n"
        "X010000Y020000D03*\n"
        "M02*\n",
        encoding="utf-8",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_rotated_flash(
        1.0,
        2.0,
        0.6,
        0.3,
        "O",
        rotation_deg=30.0,
    ).geometry

    assert result.pads == []
    assert len(result.regions) == 1
    actual = region_shape(result.regions[0])
    assert actual.symmetric_difference(expected).area == pytest.approx(
        0.0,
        abs=1e-12,
    )
    assert any(
        evidence.kind == "gerber_flash_polygonization"
        and "method=rotated_inscribed_chords" in evidence.detail
        and "rotation_deg_ccw=30" in evidence.detail
        and "max_chord_error_mm=0.005" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_nonorthogonal_flash_rotation_composes_with_whole_image_rotation(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%LR45*%\n"
        "%IR90*%\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_rotated_flash(
        -2.0,
        1.0,
        0.6,
        0.3,
        "R",
        rotation_deg=135.0,
    ).geometry

    actual = region_shape(result.regions[0])
    assert actual.symmetric_difference(expected).area == pytest.approx(
        0.0,
        abs=1e-12,
    )
    assert any(
        evidence.kind == "gerber_flash_polygonization"
        and "rotation_deg_ccw=135" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )
