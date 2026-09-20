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
        raise ValueError("segment net ordinal must be an integer")
    return node[1]


def read_segments(root):
    out = []
    for segment in children(root, "segment"):
        start = child(segment, "start")
        end = child(segment, "end")
        width = child(segment, "width")
        layer = child(segment, "layer")
        net = child(segment, "net")
        uuid = child(segment, "uuid")
        out.append(
            {
                "start": _xy(start),
                "end": _xy(end),
                "width": float(width[1]),
                "layer": str(layer[1]),
                "net": _net_ordinal(net),
                "uuid": str(uuid[1]) if uuid and len(uuid) >= 2 else None,
            }
        )
    return out
