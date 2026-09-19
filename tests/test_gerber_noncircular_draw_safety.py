from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.geometry_kernel import region_shape
from photonx_eda_pcb.gerber_image import polygonize_aperture_track
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


HEADER = """%FSLAX24Y24*%
%MOMM*%
%ADD10R,0.600X0.300*%
%ADD11C,0.200*%
%ADD12O,0.600X0.300*%
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(HEADER + body + "M02*\n", encoding="utf-8")
    return path


def _rectangle(x0: str, y0: str, x1: str, y1: str) -> str:
    return (
        "G36*\n"
        f"X{x0}Y{y0}D02*\n"
        f"X{x1}Y{y0}D01*\n"
        f"X{x1}Y{y1}D01*\n"
        f"X{x0}Y{y1}D01*\n"
        f"X{x0}Y{y0}D01*\n"
        "G37*\n"
    )


def test_rectangular_linear_draw_is_materialized_as_exact_region(tmp_path: Path):
    path = _write(
        tmp_path,
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks == []
    assert len(result.regions) == 1
    region = result.regions[0]
    assert region_shape(region).area == pytest.approx(0.48)
    assert any(
        evidence.kind == "gerber_track_polygonization"
        and "aperture_shape=R" in evidence.detail
        and "method=convex_sweep_exact" in evidence.detail
        and "approximated=false" in evidence.detail
        for evidence in region.provenance.evidence
    )

    report = preflight(path)
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_obround_linear_draw_matches_bounded_polygon_sweep(tmp_path: Path):
    path = _write(
        tmp_path,
        "D12*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    expected = polygonize_aperture_track(
        0.0,
        0.0,
        1.0,
        0.0,
        0.6,
        0.3,
        "O",
    )

    assert result.tracks == []
    assert len(result.regions) == 1
    region = result.regions[0]
    assert region_shape(region).area == pytest.approx(expected.geometry.area)
    assert any(
        evidence.kind == "gerber_track_polygonization"
        and "aperture_shape=O" in evidence.detail
        and "method=convex_sweep_inscribed_chords" in evidence.detail
        and "max_chord_error_mm=0.005" in evidence.detail
        for evidence in region.provenance.evidence
    )


def test_noncircular_draw_still_advances_current_point(tmp_path: Path):
    path = _write(
        tmp_path,
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "D11*\n"
        "X020000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    assert len(result.tracks) == 1
    track = result.tracks[0]
    assert (track.start.x, track.start.y) == pytest.approx((1.0, 0.0))
    assert (track.end.x, track.end.y) == pytest.approx((2.0, 0.0))
    assert track.width == pytest.approx(0.2)


def test_rectangular_linear_draw_respects_orthogonal_lr_rotation(tmp_path: Path):
    path = _write(
        tmp_path,
        "D10*\n"
        "%LR90*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(0.78)
    assert any(
        evidence.kind == "gerber_aperture_rotation"
        for evidence in result.regions[0].provenance.evidence
    )


def test_nonorthogonal_rectangular_draw_rotation_remains_fail_closed(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "D10*\n"
        "%LR45*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="non-axis-aligned"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction


def test_lpc_rectangular_draw_subtracts_exact_swept_material(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "D10*\n"
        "%LPC*%\n"
        "X020000Y050000D02*\n"
        "X080000Y050000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    clear_shape = polygonize_aperture_track(
        2.0,
        5.0,
        8.0,
        5.0,
        0.6,
        0.3,
        "R",
    ).geometry

    assert result.tracks == []
    assert len(result.regions) == 1
    assert len(result.regions[0].holes) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(
        100.0 - clear_shape.area
    )
    assert any(
        evidence.kind == "gerber_track_polygonization"
        and "aperture_shape=R" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )

    report = preflight(path)
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_rectangular_flash_remains_supported_as_pad(tmp_path: Path):
    path = _write(
        tmp_path,
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    pad = result.pads[0]
    assert pad.shape == "R"
    assert pad.size_x == pytest.approx(0.6)
    assert pad.size_y == pytest.approx(0.3)
