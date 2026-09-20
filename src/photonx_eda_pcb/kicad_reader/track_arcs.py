from .query import child, children


def _xy(node):
    return (
        (float(node[1]), float(node[2]))
        if node and len(node) >= 3
        else None
    )


def _net_ordinal(node):
    if node is None:
        return None
    if len(node) != 2 or isinstance(node[1], bool) or not isinstance(node[1], int):
        raise ValueError("track arc net ordinal must be an integer")
    return node[1]


def read_track_arcs(root):
    out = []
    for arc in children(root, "arc"):
        start = child(arc, "start")
        mid = child(arc, "mid")
        end = child(arc, "end")
        width = child(arc, "width")
        layer = child(arc, "layer")
        net = child(arc, "net")
        identifier = child(arc, "uuid") or child(arc, "tstamp")
        if (
            start is None
            or mid is None
            or end is None
            or width is None
            or len(width) < 2
            or layer is None
            or len(layer) < 2
        ):
            raise ValueError("track arc requires start/mid/end/width/layer")
        out.append(
            {
                "start": _xy(start),
                "mid": _xy(mid),
                "end": _xy(end),
                "width": float(width[1]),
                "layer": str(layer[1]),
                "net": _net_ordinal(net),
                "uuid": (
                    str(identifier[1])
                    if identifier and len(identifier) >= 2
                    else None
                ),
            }
        )
    return out
