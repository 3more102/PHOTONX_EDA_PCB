from .nets import read_net_reference
from .query import child, children


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
                "net": read_net_reference(net, context="via net"),
            }
        )
    return out
