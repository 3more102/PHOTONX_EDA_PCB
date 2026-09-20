from math import isfinite

from .query import child


def _optional_xy(node, name, *, label):
    item = child(node, name) if node is not None else None
    if item is None:
        return None
    if len(item) != 3:
        raise ValueError(f"{label} must contain two numeric values")
    values = (float(item[1]), float(item[2]))
    if not all(isfinite(value) for value in values):
        raise ValueError(f"{label} must be finite")
    return values


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
        "aux_axis_origin": _optional_xy(
            setup,
            "aux_axis_origin",
            label="aux_axis_origin",
        ),
        "grid_origin": _optional_xy(
            setup,
            "grid_origin",
            label="grid_origin",
        ),
        "pcbplotparams_present": bool(
            setup is not None and child(setup, "pcbplotparams") is not None
        ),
        "stackup_present": bool(
            setup is not None and child(setup, "stackup") is not None
        ),
    }
