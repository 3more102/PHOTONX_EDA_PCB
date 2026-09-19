import math

import pytest

from photonx_eda_pcb.gerber_image import polygonize_track


def test_horizontal_track_polygonization_has_bounded_round_caps():
    result = polygonize_track(0.0, 0.0, 4.0, 0.0, 2.0)

    assert result.approximated
    assert result.length_mm == pytest.approx(4.0)
    assert result.curved_segments % 4 == 0
    cap_segments = result.curved_segments // 2
    sagitta = 1.0 * (1.0 - math.cos(math.pi / (2.0 * cap_segments)))
    assert sagitta <= result.max_chord_error_mm
    assert result.geometry.bounds == pytest.approx((-1.0, -1.0, 5.0, 1.0))
    exact_area = 8.0 + math.pi
    assert result.geometry.area < exact_area
    assert result.geometry.area > exact_area - 0.03


def test_diagonal_track_polygonization_preserves_length_and_area():
    result = polygonize_track(0.0, 0.0, 3.0, 4.0, 2.0)

    assert result.length_mm == pytest.approx(5.0)
    exact_area = 10.0 + math.pi
    assert result.geometry.area < exact_area
    assert result.geometry.area > exact_area - 0.03
    assert result.geometry.is_valid


def test_zero_length_track_polygonizes_as_circle():
    result = polygonize_track(2.0, -1.0, 2.0, -1.0, 2.0)

    assert result.length_mm == 0.0
    assert result.curved_segments % 4 == 0
    assert result.geometry.bounds == pytest.approx((1.0, -2.0, 3.0, 0.0))
    assert result.geometry.area < math.pi


def test_track_polygonization_rejects_non_positive_width():
    with pytest.raises(ValueError, match="track width must be positive"):
        polygonize_track(0.0, 0.0, 1.0, 0.0, 0.0)


def test_track_polygonization_is_deterministic():
    first = polygonize_track(-2.0, 1.0, 4.0, 5.0, 0.35)
    second = polygonize_track(-2.0, 1.0, 4.0, 5.0, 0.35)

    assert first.length_mm == second.length_mm
    assert first.curved_segments == second.curved_segments
    assert first.geometry.equals_exact(second.geometry, tolerance=0.0)
