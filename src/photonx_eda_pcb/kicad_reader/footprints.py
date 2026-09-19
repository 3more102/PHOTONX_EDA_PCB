from .query import child, children
from .pads import read_pads


def _property_value(node, name):
    for prop in children(node, "property"):
        if len(prop) >= 3 and str(prop[1]) == name:
            return str(prop[2])
    return None


def read_footprints(root):
    out = []
    for f in children(root, "footprint"):
        at = child(f, "at")
        layer = child(f, "layer")
        uuid = child(f, "uuid")
        out.append(
            {
                "name": str(f[1]) if len(f) > 1 else "",
                "reference": _property_value(f, "Reference"),
                "uuid": str(uuid[1]) if uuid and len(uuid) >= 2 else None,
                "at": (float(at[1]), float(at[2])) if at else (0.0, 0.0),
                "angle": float(at[3]) if at and len(at) > 3 else 0.0,
                "layer": str(layer[1]) if layer else None,
                "pads": read_pads(f),
            }
        )
    return out
