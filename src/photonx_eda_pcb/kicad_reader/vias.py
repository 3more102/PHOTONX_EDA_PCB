from .query import child, children


def _net_ordinal(node):
    if node is None:
        return None
    if len(node) != 2 or isinstance(node[1], bool) or not isinstance(node[1], int):
        raise ValueError("via net ordinal must be an integer")
    return node[1]


def read_vias(root):
    out = []
    for via in children(root, "via"):
        at = child(via, "at")
        size = child(via, "size")
        drill = child(via, "drill")
        layers = child(via, "layers")
        net = child(via, "net")
        out.append(
            {
                "at": (float(at[1]), float(at[2])),
                "size": float(size[1]),
                "drill": float(drill[1]),
                "layers": tuple(map(str, layers[1:])),
                "net": _net_ordinal(net),
            }
        )
    return out
