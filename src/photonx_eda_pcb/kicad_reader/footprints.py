from .query import child, children
from .pads import read_pads
from .graphics import _is_canonical_copper_layer


def _property_value(node, name):
    for prop in children(node, "property"):
        if len(prop) >= 3 and str(prop[1]) == name:
            return str(prop[2])
    return None


def _unexpected_copper_graphics(node):
    out = []
    for index, item in enumerate(node[2:]):
        if not isinstance(item, list) or not item:
            continue
        token = str(item[0])
        if not (
            token.startswith("fp_")
            or token in {"property", "zone"}
        ):
            continue
        layer = child(item, "layer")
        if not layer or len(layer) < 2:
            continue
        layer_name = str(layer[1])
        if not _is_canonical_copper_layer(layer_name):
            continue
        uuid = child(item, "uuid")
        out.append(
            {
                "type": token,
                "layer": layer_name,
                "uuid": str(uuid[1]) if uuid and len(uuid) >= 2 else None,
                "child_index": index,
            }
        )
    return out


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
                "unexpected_copper_graphics": _unexpected_copper_graphics(f),
            }
        )
    return out
