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


def _optional_float(node, name, *, label):
    item = child(node, name) if node is not None else None
    if item is None:
        return None
    if len(item) != 2:
        raise ValueError(f"{label} must contain one numeric value")
    value = float(item[1])
    if not isfinite(value):
        raise ValueError(f"{label} must be finite")
    return value


def _optional_int(node, name, *, label):
    item = child(node, name) if node is not None else None
    if item is None:
        return None
    if len(item) != 2 or isinstance(item[1], bool) or not isinstance(item[1], int):
        raise ValueError(f"{label} must be an integer")
    return item[1]


def _optional_atom(node, name, *, label):
    item = child(node, name) if node is not None else None
    if item is None:
        return None
    if len(item) != 2 or isinstance(item[1], list):
        raise ValueError(f"{label} must contain one scalar value")
    return str(item[1])


def _optional_positional_atom(node, *, label):
    if node is None:
        return None
    values = [item for item in node[1:] if not isinstance(item, list)]
    if not values:
        return None
    if len(values) != 1:
        raise ValueError(f"{label} must contain at most one scalar value")
    return str(values[0])


def _hatch_settings(zone):
    hatch = child(zone, "hatch")
    if hatch is None:
        return None, None
    if len(hatch) != 3 or isinstance(hatch[1], list) or isinstance(hatch[2], list):
        raise ValueError("zone hatch must contain style and pitch")
    pitch = float(hatch[2])
    if not isfinite(pitch):
        raise ValueError("zone hatch pitch must be finite")
    return str(hatch[1]), pitch


def _default_true_flag(node, name, *, label):
    value = _optional_atom(node, name, label=label)
    if value is None:
        return True
    normalized = value.lower()
    if normalized == "yes":
        return True
    if normalized == "no":
        return False
    raise ValueError(f"{label} must be yes or no")


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
        connect_pads = child(zone, "connect_pads")
        hatch_style, hatch_pitch = _hatch_settings(zone)

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
                "rules": {
                    "hatch_style": hatch_style,
                    "hatch_pitch": hatch_pitch,
                    "priority": (
                        _optional_int(
                            zone,
                            "priority",
                            label="zone priority",
                        )
                        or 0
                    ),
                    "keepout": child(zone, "keepout") is not None,
                    "fill_mode": _optional_atom(
                        fill,
                        "mode",
                        label="zone fill mode",
                    ),
                    "filled_areas_thickness": _default_true_flag(
                        zone,
                        "filled_areas_thickness",
                        label="zone filled_areas_thickness",
                    ),
                    "connect_type": _optional_positional_atom(
                        connect_pads,
                        label="zone connect_pads connection type",
                    ),
                    "connect_clearance": _optional_float(
                        connect_pads,
                        "clearance",
                        label="zone connect_pads clearance",
                    ),
                    "min_thickness": _optional_float(
                        zone,
                        "min_thickness",
                        label="zone min_thickness",
                    ),
                    "thermal_gap": _optional_float(
                        fill,
                        "thermal_gap",
                        label="zone thermal_gap",
                    ),
                    "thermal_bridge_width": _optional_float(
                        fill,
                        "thermal_bridge_width",
                        label="zone thermal_bridge_width",
                    ),
                    "smoothing": _optional_atom(
                        fill,
                        "smoothing",
                        label="zone smoothing",
                    ),
                    "smoothing_radius": _optional_float(
                        fill,
                        "radius",
                        label="zone smoothing radius",
                    ),
                    "island_removal_mode": _optional_int(
                        fill,
                        "island_removal_mode",
                        label="zone island_removal_mode",
                    ),
                    "island_area_min": _optional_float(
                        fill,
                        "island_area_min",
                        label="zone island_area_min",
                    ),
                    "hatch_thickness": _optional_float(
                        fill,
                        "hatch_thickness",
                        label="zone hatch_thickness",
                    ),
                    "hatch_gap": _optional_float(
                        fill,
                        "hatch_gap",
                        label="zone hatch_gap",
                    ),
                    "hatch_orientation": _optional_float(
                        fill,
                        "hatch_orientation",
                        label="zone hatch_orientation",
                    ),
                    "hatch_smoothing_level": _optional_int(
                        fill,
                        "hatch_smoothing_level",
                        label="zone hatch_smoothing_level",
                    ),
                    "hatch_smoothing_value": _optional_float(
                        fill,
                        "hatch_smoothing_value",
                        label="zone hatch_smoothing_value",
                    ),
                    "hatch_border_algorithm": _optional_int(
                        fill,
                        "hatch_border_algorithm",
                        label="zone hatch_border_algorithm",
                    ),
                    "hatch_min_hole_area": _optional_float(
                        fill,
                        "hatch_min_hole_area",
                        label="zone hatch_min_hole_area",
                    ),
                },
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
