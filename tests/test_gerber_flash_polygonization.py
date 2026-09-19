import math

import pytest

from photonx_eda_pcb.gerber_image import polygonize_flash, polygonize_rotated_flash


def test_rectangular_flash_polygonization_is_exact():
    result = polygonize_flash(1.0, 2.0, 4.0, 2.0, "R")

    assert not result.approximated
    assert result.curved_segments == 0
    assert result.max_chord_error_mm == 0.0
    assert result.geometry.area == pytest.approx(8.0)
    assert result.geometry.bounds == pytest.approx((-1.0, 1.0, 3.0, 3.0))


def test_circular_flash_polygonization_has_explicit_chord_error_bound():
    result = polygonize_flash(0.0, 0.0, 2.0, 2.0, "C")

    assert result.approximated
    assert result.curved_segments % 4 == 0
    radius = 1.0
    sagitta = radius * (1.0 - math.cos(math.pi / result.curved_segments))
    assert sagitta <= result.max_chord_error_mm
    assert result.geometry.bounds == pytest.approx((-1.0, -1.0, 1.0, 1.0))
    assert result.geometry.area < math.pi
    assert result.geometry.area > math.pi - 0.03


def test_horizontal_obround_polygonization_preserves_exact_extrema():
    result = polygonize_flash(0.0, 0.0, 4.0, 2.0, "O")

    assert result.approximated
    assert result.curved_segments % 4 == 0
    cap_segments = result.curved_segments // 2
    sagitta = 1.0 * (1.0 - math.cos(math.pi / (2.0 * cap_segments)))
    assert sagitta <= result.max_chord_error_mm
    assert result.geometry.bounds == pytest.approx((-2.0, -1.0, 2.0, 1.0))
    exact_area = 4.0 + math.pi
    assert result.geometry.area < exact_area
    assert result.geometry.area > exact_area - 0.03


def test_vertical_obround_polygonization_preserves_exact_extrema():
    result = polygonize_flash(3.0, -2.0, 2.0, 4.0, "O")

    assert result.geometry.bounds == pytest.approx((2.0, -4.0, 4.0, 0.0))
    assert result.geometry.is_valid


def test_equal_axis_obround_uses_symmetric_circle_polygonization():
    result = polygonize_flash(0.0, 0.0, 2.0, 2.0, "O")

    assert result.approximated
    assert result.curved_segments % 4 == 0
    assert result.geometry.bounds == pytest.approx((-1.0, -1.0, 1.0, 1.0))


@pytest.mark.parametrize(
    ("size_x", "size_y", "shape", "match"),
    [
        (0.0, 1.0, "R", "dimensions must be positive"),
        (2.0, 1.0, "C", "equal X/Y"),
        (1.0, 1.0, "X", "unsupported Gerber flash shape"),
    ],
)
def test_flash_polygonization_rejects_invalid_geometry(
    size_x: float,
    size_y: float,
    shape: str,
    match: str,
):
    with pytest.raises(ValueError, match=match):
        polygonize_flash(0.0, 0.0, size_x, size_y, shape)


def test_flash_polygonization_is_deterministic():
    first = polygonize_flash(1.25, -0.75, 5.0, 1.5, "O")
    second = polygonize_flash(1.25, -0.75, 5.0, 1.5, "O")

    assert first == second
    assert first.geometry.equals_exact(second.geometry, tolerance=0.0)


def test_rotated_rectangular_flash_remains_exact():
    result = polygonize_rotated_flash(
        0.0,
        0.0,
        4.0,
        2.0,
        "R",
        rotation_deg=45.0,
    )

    assert not result.approximated
    assert result.curved_segments == 0
    assert result.geometry.is_valid
    assert result.geometry.area == pytest.approx(8.0)
    extent = 3.0 * math.sqrt(2.0)
    assert result.geometry.bounds == pytest.approx(
        (-extent / 2.0, -extent / 2.0, extent / 2.0, extent / 2.0)
    )


def test_rotated_obround_flash_retains_chord_error_metadata():
    result = polygonize_rotated_flash(
        1.0,
        -2.0,
        4.0,
        2.0,
        "O",
        rotation_deg=33.25,
    )

    assert result.approximated
    assert result.curved_segments > 0
    assert result.max_chord_error_mm == pytest.approx(0.005)
    assert result.geometry.is_valid


def test_rotated_flash_normalizes_rotation_and_is_deterministic():
    first = polygonize_rotated_flash(
        0.0,
        0.0,
        4.0,
        2.0,
        "R",
        rotation_deg=405.0,
    )
    second = polygonize_rotated_flash(
        0.0,
        0.0,
        4.0,
        2.0,
        "R",
        rotation_deg=45.0,
    )

    assert first.geometry.equals_exact(second.geometry, tolerance=0.0)


def test_rotated_flash_rejects_non_finite_rotation():
    with pytest.raises(ValueError, match="rotation must be finite"):
        polygonize_rotated_flash(
            0.0,
            0.0,
            4.0,
            2.0,
            "R",
            rotation_deg=math.inf,
        )
