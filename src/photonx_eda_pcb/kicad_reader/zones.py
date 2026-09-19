from math import isfinite

from .query import child, children


def _read_xy_ring(container, *, label):
    pts = child(container, "pts")
    if pts is None:
        raise ValueError(f"{label} is missing pts")

    out = []
    for vertex in pts[1:]:
        if not isinstance(vertex, list) or len(vertex) != 3 or vertex[0] != "xy":
            raise ValueError(f"{label} contains an unsupported vertex")
        x = float(vertex[1])
        y = float(vertex[2])
        if not isfinite(x) or not isfinite(y):
            raise ValueError(f"{label} contains a non-finite coordinate")
        out.append((x, y))

    if len(out) < 3 or len(set(out)) < 3:
        raise ValueError(f"{label} requires at least three distinct vertices")
    return tuple(out)


def _read_net_code(zone):
    net = child(zone, "net")
    if net is None:
        return None
    if len(net) != 2 or isinstance(net[1], bool) or not isinstance(net[1], int):
        raise ValueError("zone net ordinal must be an integer")
    return net[1]


def _read_filled_polygon(node):
    layer = child(node, "layer")
    return {
        "layer": str(layer[1]) if layer and len(layer) >= 2 else None,
        "points": _read_xy_ring(node, label="filled_polygon"),
    }


def read_zones(root):
    out = []
    for zone in children(root, "zone"):
        layer = child(zone, "layer")
        layers = child(zone, "layers")
        net_name = child(zone, "net_name")
        uuid = child(zone, "uuid")
        name = child(zone, "name")
        fill = child(zone, "fill")

        polygons = tuple(
            _read_xy_ring(polygon, label="zone polygon")
            for polygon in children(zone, "polygon")
        )
        if not polygons:
            raise ValueError("zone requires at least one polygon")

        out.append(
            {
                "net": _read_net_code(zone),
                "net_name": str(net_name[1]) if net_name and len(net_name) >= 2 else None,
                "layer": str(layer[1]) if layer and len(layer) >= 2 else None,
                "layers": tuple(map(str, layers[1:])) if layers else (),
                "uuid": str(uuid[1]) if uuid and len(uuid) >= 2 else None,
                "name": str(name[1]) if name and len(name) >= 2 else None,
                "fill_enabled": bool(fill and len(fill) >= 2 and str(fill[1]) == "yes"),
                "polygons": polygons,
                "outline": polygons[0],
                "holes": polygons[1:],
                "filled_polygons": tuple(
                    _read_filled_polygon(item)
                    for item in children(zone, "filled_polygon")
                ),
            }
        )
    return out
