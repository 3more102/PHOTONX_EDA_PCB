from .query import child, children


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
            }
        )
    return out
