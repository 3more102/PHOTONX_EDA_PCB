from math import cos, radians, sin

from photonx_eda_pcb.footprints.matcher import match_signature
from photonx_eda_pcb.models import PadCandidate, Point


def _pad(pad_id, x, y, drill=None):
    return PadCandidate(
        pad_id,
        Point(x, y),
        1.0,
        0.6,
        "R",
        "F.Cu",
        drill,
    )


def _rotated_grid(points, angle_deg, drill=None):
    angle = radians(angle_deg)
    c = cos(angle)
    s = sin(angle)
    return [
        _pad(
            f"P{index}",
            x * c - y * s,
            x * s + y * c,
            drill,
        )
        for index, (x, y) in enumerate(points, 1)
    ]


def test_rotated_soic8_topology_is_recognized():
    points = [
        (x, y)
        for y in (-2.5, 2.5)
        for x in (-1.905, -0.635, 0.635, 1.905)
    ]
    match = match_signature(_rotated_grid(points, 31.0))

    assert match["best"] == "SOIC8_LIKE"
    assert match["confidence"] >= 0.9
    assert match["features"]["row_count"] == 2
    assert match["features"]["row_sizes"] == (4, 4)
    assert match["features"]["pitch_cv"] < 1e-6


def test_rotated_dip8_topology_uses_drill_evidence():
    points = [
        (x, y)
        for y in (-3.81, 3.81)
        for x in (-3.81, -1.27, 1.27, 3.81)
    ]
    match = match_signature(_rotated_grid(points, 17.0, drill=0.8))

    assert match["best"] == "DIP8_LIKE"
    assert match["features"]["row_count"] == 2
    assert match["features"]["drilled_fraction"] == 1.0


def test_regular_single_row_header_is_recognized():
    pads = [_pad(f"P{i}", i * 2.54, 0.0, drill=0.9) for i in range(4)]
    match = match_signature(pads)

    assert match["best"] == "SINGLE_ROW_THT"
    assert match["features"]["row_count"] == 1
    assert match["features"]["row_sizes"] == (4,)


def test_ambiguous_signature_ranking_fails_closed():
    pads = [_pad("A", 0.0, 0.0), _pad("B", 2.0, 0.0)]
    signatures = [
        {
            "name": "A",
            "pad_count": 2,
            "drilled_max": 0.01,
            "row_count": 1,
        },
        {
            "name": "B",
            "pad_count": 2,
            "drilled_max": 0.01,
            "row_count": 1,
        },
    ]

    match = match_signature(pads, signatures=signatures)

    assert match["best"] is None
    assert match["ambiguous"] is True
    assert match["candidate_confidence"] >= 0.7
    assert match["margin"] == 0.0


def test_implausibly_large_two_pad_pitch_is_not_promoted():
    pads = [_pad("A", 0.0, 0.0), _pad("B", 100.0, 0.0)]
    match = match_signature(pads)

    assert match["best"] is None
    assert match["candidate_confidence"] == 0.0
