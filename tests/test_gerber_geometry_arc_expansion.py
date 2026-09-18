import pytest

from photonx_eda_pcb.gerber_geometry.arc import (
    ArcSpec,
    arc_points,
    segments_for_chord_error,
    validate_arc,
)
from photonx_eda_pcb.gerber_geometry.model import GeoPoint


def test_arc():
    pts = arc_points(
        ArcSpec(GeoPoint(1, 0), GeoPoint(0, 1), GeoPoint(0, 0)),
        segments=4,
    )
    assert len(pts) == 5
    assert round(pts[-1].y, 6) == 1


def test_adaptive_arc_tessellation_preserves_exact_endpoints():
    spec = ArcSpec(
        GeoPoint(1.0, 0.0),
        GeoPoint(0.0, 1.0),
        GeoPoint(0.0, 0.0),
    )
    count = segments_for_chord_error(spec, 0.005)
    pts = arc_points(spec, segments=None, max_chord_error_mm=0.005)

    assert count > 1
    assert len(pts) == count + 1
    assert pts[0] == spec.start
    assert pts[-1] == spec.end


def test_full_circle_is_not_collapsed_to_zero_length():
    spec = ArcSpec(
        GeoPoint(1.0, 0.0),
        GeoPoint(1.0, 0.0),
        GeoPoint(0.0, 0.0),
        clockwise=True,
    )
    count = segments_for_chord_error(spec, 0.005)
    pts = arc_points(spec, segments=count)

    assert count >= 4
    assert len(pts) == count + 1
    assert pts[0] == pts[-1]
    assert len(set(pts[:-1])) > 2


def test_arc_validation_rejects_inconsistent_radii():
    spec = ArcSpec(
        GeoPoint(1.0, 0.0),
        GeoPoint(0.0, 2.0),
        GeoPoint(0.0, 0.0),
    )
    with pytest.raises(ValueError):
        validate_arc(spec)
