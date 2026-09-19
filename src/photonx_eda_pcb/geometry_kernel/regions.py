from __future__ import annotations

from shapely.geometry import Polygon

from photonx_eda_pcb.models import CopperRegion


def region_shape(region: CopperRegion) -> Polygon:
    """Return the exact polygon represented by a closed CopperRegion."""
    return Polygon([(float(point.x), float(point.y)) for point in region.points])
