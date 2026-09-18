from __future__ import annotations

from shapely.geometry import Polygon


def region_shape(region):
    """Return the exact polygon represented by a CopperRegion."""
    coords = [(float(p.x), float(p.y)) for p in region.points]
    return Polygon(coords)
