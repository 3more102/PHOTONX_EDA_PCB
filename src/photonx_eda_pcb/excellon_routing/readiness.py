from dataclasses import dataclass
from math import atan2, degrees, hypot, isfinite


@dataclass(frozen=True)
class RouteExportReadiness:
    exportable: tuple[str, ...]
    omitted: tuple[str, ...]
    reasons: dict[str, str]

    @property
    def fully_resolved(self):
        return not self.omitted


def is_exact_npth_slot_route(route):
    plating = str(getattr(route, "plated", "unknown")).lower().replace("_", "-")
    if plating != "non-plated":
        return False

    points = tuple(getattr(route, "points", ()))
    if len(points) != 2:
        return False

    try:
        x0, y0 = map(float, points[0])
        x1, y1 = map(float, points[1])
        width = float(route.width_mm)
    except (TypeError, ValueError, OverflowError):
        return False

    values = (x0, y0, x1, y1, width)
    return (
        all(isfinite(value) for value in values)
        and width > 0
        and (x0, y0) != (x1, y1)
    )


def route_export_descriptor(route):
    if not is_exact_npth_slot_route(route):
        return None

    (x0, y0), (x1, y1) = route.points
    x0 = float(x0)
    y0 = float(y0)
    x1 = float(x1)
    y1 = float(y1)
    width = float(route.width_mm)
    dx = x1 - x0
    dy = y1 - y0
    centerline = hypot(dx, dy)
    long_dim = centerline + width
    return {
        "center": ((x0 + x1) / 2.0, (y0 + y1) / 2.0),
        "angle_deg": degrees(atan2(dy, dx)),
        "size": (long_dim, width),
        "drill_size": (long_dim, width),
        "layers": ("*.Cu", "*.Mask"),
        "footprint_layer": "F.Cu",
        "reference_layer": "F.SilkS",
    }


def assess_route_export_readiness(routes):
    exportable = []
    omitted = []
    reasons = {}
    for route in sorted(routes, key=lambda item: item.id):
        if is_exact_npth_slot_route(route):
            exportable.append(route.id)
        else:
            omitted.append(route.id)
            reasons[route.id] = "KICAD_ARBITRARY_ROUTE_UNSUPPORTED"
    return RouteExportReadiness(
        tuple(exportable),
        tuple(omitted),
        reasons,
    )
