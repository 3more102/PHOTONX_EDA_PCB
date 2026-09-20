from .query import children


def read_nets(root):
    out = []
    for net in children(root, "net"):
        if len(net) < 3:
            continue
        if isinstance(net[1], bool) or not isinstance(net[1], int):
            raise ValueError("net table ordinal must be an integer")
        out.append({"code": net[1], "name": str(net[2])})
    return out
