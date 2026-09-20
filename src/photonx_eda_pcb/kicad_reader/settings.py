from math import isfinite

from .query import child


def _optional_float(node, name, *, label):
    item = child(node, name) if node is not None else None
    if item is None:
        return None
    if len(item) != 2:
        raise ValueError(f"{label} must contain one numeric value")
    value = float(item[1])
    if not isfinite(value):
        raise ValueError(f"{label} must be finite")
    return value


def read_board_settings(root):
    general = child(root, "general")
    setup = child(root, "setup")
    return {
        "thickness": _optional_float(
            general,
            "thickness",
            label="board thickness",
        ),
        "pad_to_mask_clearance": _optional_float(
            setup,
            "pad_to_mask_clearance",
            label="pad_to_mask_clearance",
        ),
    }
