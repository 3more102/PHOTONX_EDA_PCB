from .nets import read_net_reference
from .query import child, children


def _xy(node):
    return (float(node[1]), float(node[2])) if node and len(node) >= 3 else None


def read_segments(root):
    out = []
    for segment in children(root, "segment"):
        net = child(segment, "net")
        out.append(
            {
                "start": _xy(child(segment, "start")),
                "end": _xy(child(segment, "end")),
                "width": float(child(segment, "width")[1]),
                "layer": str(child(segment, "layer")[1]),
                "net": read_net_reference(net, context="segment net"),
            }
        )
    return out
