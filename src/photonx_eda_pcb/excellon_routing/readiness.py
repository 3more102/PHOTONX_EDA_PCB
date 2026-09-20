from dataclasses import dataclass
from math import atan2, degrees, hypot, isfinite

from photonx_eda_pcb.mechanical_features import SlotFeature


@dataclass(frozen=True)
class RouteExportReadiness:
    exportable: tuple[str, ...]
    omitted: tuple[str, ...]
    reasons: dict[str, str]

    @property
    def fully_resolved(self):
        return not self.omitted


def _route_geometry(route):
    points = tuple(getattr(route, "points", ()))
    if len(points) != 2:
        return None

    try:
        x0, y0 = map(float, points[0])
        x1, y1 = map(float, points[1])
        width = float(route.width_mm)
    except (TypeError, ValueError, OverflowError):
        return None

    values = (x0, y0, x1, y1, width)
    if (
        not all(isfinite(value) for value in values)
        or width <= 0
        or (x0, y0) == (x1, y1)
    ):
        return None

    dx = x1 - x0
    dy = y1 - y0
    centerline = hypot(dx, dy)
    long_dim = centerline + width
    return {
        "start": (x0, y0),
        "end": (x1, y1),
        "center": ((x0 + x1) / 2.0, (y0 + y1) / 2.0),
        "angle_deg": degrees(atan2(dy, dx)),
        "size": (long_dim, width),
        "drill_size": (long_dim, width),
    }


def is_exact_npth_slot_route(route):
    plating = str(getattr(route, "plated", "unknown")).lower().replace("_", "-")
    return plating == "non-plated" and _route_geometry(route) is not None


def _route_slot_feature(route):
    geometry = _route_geometry(route)
    if geometry is None:
        return None
    return SlotFeature(
        str(route.id),
        geometry["start"],
        geometry["end"],
        float(route.width_mm),
        str(getattr(route, "plated", "unknown")),
        getattr(route, "tool", None),
        getattr(route, "provenance", None),
        getattr(route, "layer_span", None),
        bool(getattr(route, "span_proven", False)),
        getattr(route, "x2_layer_span", None),
        getattr(route, "x2_span_kind", None),
    )


def _net_is_unambiguous(board, net_id):
    if net_id is None:
        return False
    return sum(1 for net in getattr(board, "nets", ()) if net.id == net_id) == 1


def _declared_copper_layers(board):
    if board is None:
        return ()
    from photonx_eda_pcb.exporters.kicad_policy import kicad_board_layer_specs

    return tuple(
        str(row["name"])
        for row in kicad_board_layer_specs(board)
        if str(row["name"]).endswith(".Cu")
    )


def _plated_route_span_reason(board, route):
    if board is None:
        return "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"

    if getattr(route, "x2_layer_span", None) is None:
        return "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"

    if not bool(getattr(route, "span_proven", False)) or getattr(
        route, "layer_span", None
    ) is None:
        return "KICAD_PLATED_ROUTE_SPAN_UNPROVEN"

    declared_layers = _declared_copper_layers(board)
    if len(declared_layers) < 2:
        return "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"

    if tuple(route.layer_span) != (declared_layers[0], declared_layers[-1]):
        return "KICAD_PLATED_ROUTE_PARTIAL_DEPTH_UNREPRESENTABLE"

    return "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"


def _plated_route_padstack(board, route):
    # Lazy import avoids a models -> excellon_routing -> plated-slot -> geometry
    # -> models cycle during package initialization.
    from photonx_eda_pcb.plated_slot_inference import infer_plated_slot_padstack

    plating = str(getattr(route, "plated", "unknown")).lower().replace("_", "-")
    if board is None or plating != "plated":
        return None

    slot = _route_slot_feature(route)
    if slot is None:
        return None

    inference = infer_plated_slot_padstack(board, slot)
    padstack = inference.padstack
    if padstack is None or not _net_is_unambiguous(board, padstack.net_id):
        return None

    declared_layers = _declared_copper_layers(board)
    padstack_layers = tuple(str(layer) for layer in padstack.layers)
    if len(declared_layers) < 2 or padstack_layers != declared_layers:
        return None

    if getattr(route, "x2_layer_span", None) is not None:
        if (
            not bool(getattr(route, "span_proven", False))
            or getattr(route, "layer_span", None) is None
            or tuple(route.layer_span)
            != (declared_layers[0], declared_layers[-1])
        ):
            return None

    return padstack


def _pad_shape_name(shape):
    value = str(shape or "").upper()
    if value == "C":
        return "circle"
    if value == "O":
        return "oval"
    if value == "R":
        return "rect"
    return None


def route_export_descriptor(route, board=None):
    geometry = _route_geometry(route)
    if geometry is None:
        return None

    plating = str(getattr(route, "plated", "unknown")).lower().replace("_", "-")
    if plating == "non-plated":
        return {
            "kind": "npth",
            "footprint_name": "PHOTONX:RecoveredNPTHRoute",
            "center": geometry["center"],
            "angle_deg": geometry["angle_deg"],
            "size": geometry["size"],
            "drill_size": geometry["drill_size"],
            "layers": ("*.Cu", "*.Mask"),
            "footprint_layer": "F.Cu",
            "reference_layer": "F.SilkS",
            "pad_number": "",
            "pad_kind": "np_thru_hole",
            "pad_shape": "oval",
            "net_id": None,
        }

    if plating != "plated":
        return None

    padstack = _plated_route_padstack(board, route)
    if padstack is None:
        return None
    pad_shape = _pad_shape_name(padstack.pad_shape)
    if pad_shape is None:
        return None

    return {
        "kind": "plated",
        "footprint_name": "PHOTONX:RecoveredPlatedRoute",
        "center": padstack.center,
        "angle_deg": padstack.angle_deg,
        "size": padstack.pad_size,
        "drill_size": padstack.drill_size,
        "layers": (*padstack.layers, "*.Mask"),
        "footprint_layer": "F.Cu",
        "reference_layer": "F.SilkS",
        "pad_number": "1",
        "pad_kind": "thru_hole",
        "pad_shape": pad_shape,
        "net_id": padstack.net_id,
    }


def assess_route_export_readiness(routes, board=None):
    exportable = []
    omitted = []
    reasons = {}
    for route in sorted(routes, key=lambda item: item.id):
        descriptor = route_export_descriptor(route, board)
        if descriptor is not None:
            exportable.append(route.id)
            continue

        omitted.append(route.id)
        plating = str(getattr(route, "plated", "unknown")).lower().replace("_", "-")
        if plating == "plated" and _route_geometry(route) is not None:
            reasons[route.id] = _plated_route_span_reason(board, route)
        else:
            reasons[route.id] = "KICAD_ARBITRARY_ROUTE_UNSUPPORTED"

    return RouteExportReadiness(
        tuple(exportable),
        tuple(omitted),
        reasons,
    )
