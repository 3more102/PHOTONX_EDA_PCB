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


def _is_backdrill(route):
    function = str(
        getattr(route, "x2_aperture_function", "") or ""
    ).lower().replace("_", "").replace("-", "")
    return function == "backdrill"


def is_exact_npth_slot_route(route):
    plating = str(getattr(route, "plated", "unknown")).lower().replace("_", "-")
    return (
        not _is_backdrill(route)
        and plating == "non-plated"
        and _route_geometry(route) is not None
    )


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
        getattr(route, "span_proven", False) is True,
        getattr(route, "x2_layer_span", None),
        getattr(route, "x2_span_kind", None),
        getattr(route, "x2_aperture_function", None),
    )


def _net_is_unambiguous(board, net_id):
    if net_id is None:
        return False
    return sum(1 for net in getattr(board, "nets", ()) if net.id == net_id) == 1


def _plated_route_span_rejection(route):
    kind = str(getattr(route, "x2_span_kind", "") or "").lower()
    raw_span = getattr(route, "x2_layer_span", None)
    span = getattr(route, "layer_span", None)
    span_proven = getattr(route, "span_proven", False) is True

    if raw_span is not None and not span_proven:
        return "KICAD_PLATED_ROUTE_SPAN_UNPROVEN"

    if span_proven:
        if not isinstance(span, (list, tuple)) or len(span) != 2:
            return "KICAD_PLATED_ROUTE_SPAN_UNPROVEN"
        endpoints = {str(span[0]), str(span[1])}
        if endpoints != {"F.Cu", "B.Cu"}:
            return "KICAD_PLATED_ROUTE_PARTIAL_SPAN_UNSUPPORTED"
        if kind in {"blind", "buried"}:
            return "KICAD_PLATED_ROUTE_X2_KIND_MISMATCH"

    if kind in {"blind", "buried"}:
        return "KICAD_PLATED_ROUTE_SPAN_UNPROVEN"
    return None


def _plated_route_padstack(board, route):
    # KiCad recovered routed slots use a thru_hole pad. Export is therefore
    # limited to full-stack routes; partial-depth X2 Blind/Buried routing
    # remains explicit source evidence instead of being widened to all copper.
    from photonx_eda_pcb.exporters.kicad_policy import declared_copper_layer_names
    from photonx_eda_pcb.plated_slot_inference import infer_plated_slot_padstack

    plating = str(getattr(route, "plated", "unknown")).lower().replace("_", "-")
    if board is None or plating != "plated":
        return None, "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"

    span_rejection = _plated_route_span_rejection(route)
    if span_rejection is not None:
        return None, span_rejection

    slot = _route_slot_feature(route)
    if slot is None:
        return None, "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"
    inference = infer_plated_slot_padstack(board, slot)
    padstack = inference.padstack
    if padstack is None or not _net_is_unambiguous(board, padstack.net_id):
        return None, "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"

    declared_layers = set(declared_copper_layer_names(board))
    padstack_layers = tuple(str(layer) for layer in padstack.layers)
    if (
        not padstack_layers
        or not {"F.Cu", "B.Cu"}.issubset(set(padstack_layers))
        or set(padstack_layers) != declared_layers
    ):
        return None, "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"
    return padstack, None


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
    if geometry is None or _is_backdrill(route):
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

    padstack, _reason = _plated_route_padstack(board, route)
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
        if _is_backdrill(route):
            reasons[route.id] = "KICAD_BACKDRILL_UNSUPPORTED"
        elif plating == "plated" and _route_geometry(route) is not None:
            _padstack, reason = _plated_route_padstack(board, route)
            reasons[route.id] = (
                reason or "KICAD_PLATED_ROUTE_PADSTACK_UNPROVEN"
            )
        else:
            reasons[route.id] = "KICAD_ARBITRARY_ROUTE_UNSUPPORTED"

    return RouteExportReadiness(
        tuple(exportable),
        tuple(omitted),
        reasons,
    )
