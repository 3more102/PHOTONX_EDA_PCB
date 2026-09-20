from math import cos, radians, sin

from photonx_eda_pcb.footprints.matcher import match_signature
from photonx_eda_pcb.models import PadCandidate, Point


def _pad(pad_id, x, y):
    return PadCandidate(
        pad_id,
        Point(x, y),
        0.45,
        0.45,
        "C",
        "F.Cu",
    )


def _rotated(points, angle_deg):
    angle = radians(angle_deg)
    c = cos(angle)
    s = sin(angle)
    return [
        _pad(
            f"P{index}",
            x * c - y * s,
            x * s + y * c,
        )
        for index, (x, y) in enumerate(points, 1)
    ]


def test_rotated_square_grid_array_is_recognized():
    points = [(x * 0.8, y * 0.8) for x in range(4) for y in range(4)]
    match = match_signature(_rotated(points, 27.0))

    assert match["best"] == "GRID_ARRAY_SMD"
    assert match["confidence"] >= 0.70
    assert match["features"]["grid_shape"] == (4, 4)
    assert match["features"]["grid_occupancy"] > 0.99
    assert match["features"]["symmetry_score"] > 0.99


def test_sparse_irregular_array_fails_closed():
    points = [
        (0.0, 0.0),
        (0.8, 0.0),
        (2.4, 0.0),
        (0.0, 0.8),
        (1.6, 0.8),
        (2.4, 0.8),
        (0.8, 1.6),
        (2.4, 1.6),
        (0.0, 2.4),
        (1.6, 2.4),
    ]
    match = match_signature(_rotated(points, 23.0))

    assert match["best"] is None
    assert match["features"]["grid_occupancy"] < 0.80


def test_exact_soic8_keeps_precedence_over_generic_geometry():
    points = [
        (x, y)
        for y in (-2.5, 2.5)
        for x in (-1.905, -0.635, 0.635, 1.905)
    ]
    match = match_signature(_rotated(points, 19.0))

    assert match["best"] == "SOIC8_LIKE"
    assert match["confidence"] >= 0.90
