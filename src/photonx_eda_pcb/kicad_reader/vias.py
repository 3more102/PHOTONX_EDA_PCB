from .query import child, children


def _net_ordinal(node):
    if node is None:
        return None
    if len(node) != 2 or isinstance(node[1], bool) or not isinstance(node[1], int):
        raise ValueError("via net ordinal must be an integer")
    return node[1]


def _via_type(via):
    if len(via) > 1 and isinstance(via[1], str):
        if via[1] in {"blind", "micro"}:
            return via[1]
    return "through"


def read_vias(root):
    out = []
    for via in children(root, "via"):
        at = child(via, "at")
        size = child(via, "size")
        drill = child(via, "drill")
        layers = child(via, "layers")
        net = child(via, "net")
        object_uuid = child(via, "uuid")
        out.append(
            {
                "type": _via_type(via),
                "at": (float(at[1]), float(at[2])),
                "size": float(size[1]),
                "drill": float(drill[1]),
                "layers": tuple(map(str, layers[1:])),
                "net": _net_ordinal(net),
                "uuid": None if object_uuid is None else str(object_uuid[1]),
                "locked": child(via, "locked") is not None,
                "remove_unused_layers": child(via, "remove_unused_layers") is not None,
                "keep_end_layers": child(via, "keep_end_layers") is not None,
                "free": child(via, "free") is not None,
            }
        )
    return out
