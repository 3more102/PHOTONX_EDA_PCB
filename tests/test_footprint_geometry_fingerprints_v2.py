from math import cos, radians, sin
from types import SimpleNamespace

from photonx_eda_pcb.footprints.matcher import match_signature


def _pads(points, drilled=False):
    drill = 0.8 if drilled else None
    return [
        SimpleNamespace(
            id=str(index),
            center=SimpleNamespace(x=x, y=y),
            drill=drill,
        )
        for index, (x, y) in enumerate(points)
    ]


def _rotate(points, angle_deg):
    angle = radians(angle_deg)
    c, s = cos(angle), sin(angle)
    return [(x * c - y * s, x * s + y * c) for x, y in points]


def test_unmatched_signature_fails_closed():
    result = match_signature(_pads([(0, 0), (1.2, 0.3), (3.1, 2.7)]))
    assert result["best"] is None
    assert result["confidence"] == 0.0


def test_rotated_dual_row_tht_geometry_family():
    base = [(i * 2.54, 0.0) for i in range(7)]
    base += [(i * 2.54, 7.62) for i in range(7)]
    result = match_signature(_pads(_rotate(base, 31.0), drilled=True))
    assert result["best"] == "DUAL_ROW_THT_LIKE"
    assert result["features"]["two_row_score"] > 0.99
    assert result["features"]["symmetry_score"] > 0.99


def test_rotated_grid_array_smd_geometry_family():
    base = [(x * 0.8, y * 0.8) for x in range(4) for y in range(4)]
    result = match_signature(_pads(_rotate(base, 27.0)))
    assert result["best"] == "GRID_ARRAY_SMD_LIKE"
    assert result["features"]["grid_shape"] == (4, 4)
    assert result["features"]["grid_occupancy"] > 0.99


def test_exact_soic8_signature_keeps_precedence():
    base = [(i * 1.27, 0.0) for i in range(4)]
    base += [(i * 1.27, 5.4) for i in range(4)]
    result = match_signature(_pads(_rotate(base, 19.0)))
    assert result["best"] == "SOIC8_LIKE"
    assert result["confidence"] >= 0.8
