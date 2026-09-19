import math

import pytest

from photonx_eda_pcb.gerber_image import polygonize_aperture_track, polygonize_track


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


def test_rectangular_aperture_track_sweep_is_exact():
    result = polygonize_aperture_track(
        0.0, 0.0, 1.0, 0.0, 0.6, 0.3, "R"
    )

    assert result.shape == "R"
    assert not result.approximated
    assert result.curved_segments == 0
    assert result.max_chord_error_mm == 0.0
    assert result.length_mm == pytest.approx(1.0)
    assert result.geometry.bounds == pytest.approx((-0.3, -0.15, 1.3, 0.15))
    assert result.geometry.area == pytest.approx(0.48)


def test_obround_aperture_track_sweep_is_bounded_and_deterministic():
    first = polygonize_aperture_track(
        0.0, 0.0, 1.0, 0.0, 0.6, 0.3, "O"
    )
    second = polygonize_aperture_track(
        0.0, 0.0, 1.0, 0.0, 0.6, 0.3, "O"
    )

    exact_area = 1.3 * 0.3 + math.pi * 0.15**2
    assert first.approximated
    assert first.max_chord_error_mm == pytest.approx(0.005)
    assert first.geometry.is_valid
    assert first.geometry.area < exact_area
    assert first.geometry.area > exact_area - 0.01
    assert first.geometry.equals_exact(second.geometry, tolerance=0.0)


def test_circular_aperture_track_wrapper_matches_capsule_polygonizer():
    generic = polygonize_aperture_track(
        0.0, 0.0, 3.0, 4.0, 2.0, 2.0, "C"
    )
    circular = polygonize_track(0.0, 0.0, 3.0, 4.0, 2.0)

    assert generic.length_mm == circular.length_mm
    assert generic.curved_segments == circular.curved_segments
    assert generic.geometry.equals_exact(circular.geometry, tolerance=0.0)


def test_rectangular_aperture_track_supports_arbitrary_rotation_exactly():
    result = polygonize_aperture_track(
        0.0,
        0.0,
        1.0,
        0.0,
        0.6,
        0.3,
        "R",
        rotation_deg=45.0,
    )

    expected_vertical_extent = (0.6 + 0.3) / math.sqrt(2.0)
    expected_area = 0.6 * 0.3 + expected_vertical_extent
    assert result.rotation_deg == pytest.approx(45.0)
    assert not result.approximated
    assert result.curved_segments == 0
    assert result.geometry.is_valid
    assert result.geometry.area == pytest.approx(expected_area)


def test_obround_aperture_track_rotation_is_deterministic():
    first = polygonize_aperture_track(
        -0.5,
        1.0,
        2.5,
        1.0,
        0.6,
        0.3,
        "O",
        rotation_deg=33.25,
    )
    second = polygonize_aperture_track(
        -0.5,
        1.0,
        2.5,
        1.0,
        0.6,
        0.3,
        "O",
        rotation_deg=33.25,
    )

    assert first.rotation_deg == pytest.approx(33.25)
    assert first.approximated
    assert first.geometry.equals_exact(second.geometry, tolerance=0.0)


def test_aperture_track_rotation_normalizes_degrees():
    result = polygonize_aperture_track(
        0.0,
        0.0,
        1.0,
        0.0,
        0.6,
        0.3,
        "R",
        rotation_deg=405.0,
    )

    assert result.rotation_deg == pytest.approx(45.0)


def test_aperture_track_rejects_non_finite_rotation():
    with pytest.raises(ValueError, match="rotation must be finite"):
        polygonize_aperture_track(
            0.0,
            0.0,
            1.0,
            0.0,
            0.6,
            0.3,
            "R",
            rotation_deg=math.inf,
        )
