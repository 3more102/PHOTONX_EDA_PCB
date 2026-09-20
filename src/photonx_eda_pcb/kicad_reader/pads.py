from .query import child, children


def _optional_float(node, name):
    item = child(node, name)
    if item is None:
        return None
    if len(item) != 2:
        raise ValueError(f"pad {name} must contain one numeric value")
    return float(item[1])


def _optional_int_alias(node, *names):
    found = [child(node, name) for name in names]
    found = [item for item in found if item is not None]
    if not found:
        return None
    if len(found) != 1:
        raise ValueError("pad zone connection override is ambiguous")
    item = found[0]
    if len(item) != 2 or isinstance(item[1], bool) or not isinstance(item[1], int):
        raise ValueError("pad zone connection override must be an integer")
    return item[1]


def _copper_overrides(node):
    return {
        "clearance": _optional_float(node, "clearance"),
        "zone_connect": _optional_int_alias(
            node,
            "zone_connect",
            "zone_connection",
        ),
        "thermal_width": _optional_float(node, "thermal_width"),
        "thermal_gap": _optional_float(node, "thermal_gap"),
        "remove_unused_layer": child(node, "remove_unused_layer") is not None,
        "keep_end_layers": child(node, "keep_end_layers") is not None,
    }


def _pad_property(node):
    item = child(node, "property")
    if item is None:
        return None
    if len(item) != 2:
        raise ValueError("pad property must contain one value")
    return str(item[1])


def _read_drill(drill):
    if not drill:
        return {
            "drill": None,
            "drill_shape": None,
            "drill_size": None,
            "drill_offset": (0.0, 0.0),
        }
    offset = child(drill, "offset")
    off = (
        (float(offset[1]), float(offset[2]))
        if offset and len(offset) >= 3
        else (0.0, 0.0)
    )
    if len(drill) > 1 and str(drill[1]) == "oval":
        if len(drill) < 4:
            raise ValueError("oval drill requires two dimensions")
        size = (float(drill[2]), float(drill[3]))
        return {
            "drill": min(size),
            "drill_shape": "oval",
            "drill_size": size,
            "drill_offset": off,
        }
    d = float(drill[1])
    return {
        "drill": d,
        "drill_shape": "round",
        "drill_size": (d, d),
        "drill_offset": off,
    }


def _read_net(net):
    if net is None:
        return None, None
    if len(net) < 2 or isinstance(net[1], bool) or not isinstance(net[1], int):
        raise ValueError("pad net ordinal must be an integer")
    name = str(net[2]) if len(net) >= 3 else None
    return net[1], name


def read_pads(footprint):
    out = []
    for pad in children(footprint, "pad"):
        at = child(pad, "at")
        size = child(pad, "size")
        drill = child(pad, "drill")
        layers = child(pad, "layers")
        net_code, net_name = _read_net(child(pad, "net"))
        uuid = child(pad, "uuid")
        info = _read_drill(drill)
        out.append(
            {
                "number": str(pad[1]),
                "kind": str(pad[2]),
                "shape": str(pad[3]),
                "at": (float(at[1]), float(at[2])) if at else (0.0, 0.0),
                "angle": float(at[3]) if at and len(at) > 3 else 0.0,
                "size": (float(size[1]), float(size[2])) if size else None,
                "drill": info["drill"],
                "drill_shape": info["drill_shape"],
                "drill_size": info["drill_size"],
                "drill_offset": info["drill_offset"],
                "layers": tuple(map(str, layers[1:])) if layers else (),
                "net": net_code,
                "net_name": net_name,
                "uuid": str(uuid[1]) if uuid and len(uuid) >= 2 else None,
                "property": _pad_property(pad),
                "copper_overrides": _copper_overrides(pad),
            }
        )
    return out
