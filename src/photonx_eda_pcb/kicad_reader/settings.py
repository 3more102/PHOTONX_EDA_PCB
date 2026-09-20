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
        "solder_mask_min_width": _optional_float(
            setup,
            "solder_mask_min_width",
            label="solder_mask_min_width",
        ),
        "pad_to_paste_clearance": _optional_float(
            setup,
            "pad_to_paste_clearance",
            label="pad_to_paste_clearance",
        ),
        "pad_to_paste_clearance_ratio": _optional_float(
            setup,
            "pad_to_paste_clearance_ratio",
            label="pad_to_paste_clearance_ratio",
        ),
        "stackup_present": bool(
            setup is not None and child(setup, "stackup") is not None
        ),
    }
