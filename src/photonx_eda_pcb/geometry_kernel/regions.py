from __future__ import annotations

from shapely.geometry import Polygon

from photonx_eda_pcb.models import CopperRegion


def region_shape(region: CopperRegion) -> Polygon:
    """Return the exact polygon represented by a CopperRegion shell and holes."""
    shell = [(float(point.x), float(point.y)) for point in region.points]
    holes = [
        [(float(point.x), float(point.y)) for point in ring]
        for ring in getattr(region, "holes", ())
    ]
    return Polygon(shell, holes)
