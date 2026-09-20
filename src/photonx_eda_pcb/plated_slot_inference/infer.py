from math import hypot

from .model import PlatedSlotPadstack, PadstackInference
from .contacts import slot_pad_contacts
from photonx_eda_pcb.mechanical_features.measure import slot_geometry_descriptor
from photonx_eda_pcb.geometry_kernel import pad_shape
from photonx_eda_pcb.mechanical_features.geometry import slot_shape


def _near(a, b, tol):
    return abs(float(a) - float(b)) <= float(tol)


def _orthogonal(angle, tol_deg=1e-3):
    a = float(angle) % 180
    if min(abs(a), abs(a - 90), abs(a - 180)) <= tol_deg:
        return 0 if abs(a) < tol_deg or abs(a - 180) < tol_deg else 90
    return None


def _layer_key(layer):
    if layer == "F.Cu":
        return (0, layer)
    if layer == "B.Cu":
        return (999, layer)
    if layer.startswith("In") and layer.endswith(".Cu"):
        try:
            return (int(layer[2:-3]), layer)
        except ValueError:
            pass
    return (500, layer)


def _is_copper_layer(layer):
    if layer in {"F.Cu", "B.Cu"}:
        return True
    if not (
        isinstance(layer, str)
        and layer.startswith("In")
        and layer.endswith(".Cu")
    ):
        return False
    try:
        return int(layer[2:-3]) >= 1
    except ValueError:
        return False


def _declared_x2_copper_layers(board):
    metadata = getattr(board, "metadata", {})
    if not isinstance(metadata, dict):
        return None
    x2 = metadata.get("x2_copper_stackup")
    if not isinstance(x2, dict) or x2.get("status") != "declared":
        return None
    layers = x2.get("layers")
    if not isinstance(layers, (list, tuple)) or len(layers) < 2:
        return ()
    normalized = tuple(str(layer) for layer in layers)
    if (
        len(set(normalized)) != len(normalized)
        or not all(_is_copper_layer(layer) for layer in normalized)
    ):
        return ()
    return normalized


def _target_layers(slot, declared_layers, by_layer):
    explicit_span = getattr(slot, "x2_layer_span", None)
    if explicit_span is None:
        if declared_layers is not None:
            return tuple(declared_layers), None
        return tuple(sorted(by_layer, key=_layer_key)), None

    if (
        not bool(getattr(slot, "span_proven", False))
        or getattr(slot, "layer_span", None) is None
    ):
        return None, "SLOT_X2_LAYER_SPAN_UNRESOLVED"

    canonical_span = tuple(slot.layer_span)
    if len(canonical_span) != 2 or canonical_span[0] == canonical_span[1]:
        return None, "SLOT_X2_LAYER_SPAN_INVALID"

    if declared_layers is not None:
        order = tuple(declared_layers)
    else:
        order = tuple(sorted(by_layer, key=_layer_key))

    if any(layer not in order for layer in canonical_span):
        return None, "SLOT_X2_LAYER_SPAN_OUTSIDE_STACKUP"

    start = order.index(canonical_span[0])
    end = order.index(canonical_span[1])
    if start > end:
        start, end = end, start
    target = order[start : end + 1]
    if len(target) < 2:
        return None, "SLOT_X2_LAYER_SPAN_INVALID"
    return target, None


def infer_plated_slot_padstack(board, slot, tolerance_mm=.03):
    if str(slot.plated).lower().replace("_", "-") != "plated":
        return PadstackInference(slot.id, None, ("SLOT_NOT_PROVEN_PLATED",))

    desc = slot_geometry_descriptor(slot)
    orth = _orthogonal(desc["angle_deg"])
    if orth is None:
        return PadstackInference(slot.id, None, ("SLOT_ANGLE_NON_ORTHOGONAL",))

    contacts = slot_pad_contacts(board, slot, tolerance_mm)
    covering = [
        pad
        for pad in contacts
        if _is_copper_layer(getattr(pad, "layer", None))
        and pad_shape(pad).buffer(tolerance_mm).covers(slot_shape(slot))
    ]
    if not covering:
        return PadstackInference(slot.id, None, ("SLOT_NO_COPPER_PAD_COVERAGE",))

    by_layer = {}
    for pad in covering:
        by_layer.setdefault(pad.layer, []).append(pad)

    declared_layers = _declared_x2_copper_layers(board)
    if declared_layers == ():
        return PadstackInference(
            slot.id,
            None,
            ("SLOT_X2_COPPER_STACKUP_INVALID",),
        )

    target_layers, target_error = _target_layers(slot, declared_layers, by_layer)
    if target_error is not None:
        return PadstackInference(slot.id, None, (target_error,))

    missing_layers = [
        layer for layer in target_layers if layer not in by_layer
    ]
    if missing_layers:
        return PadstackInference(
            slot.id,
            None,
            ("SLOT_X2_COPPER_LAYER_COVERAGE_MISMATCH",),
        )

    selected = [
        sorted(
            by_layer[layer],
            key=lambda pad: (pad_shape(pad).area, pad.id),
        )[0]
        for layer in target_layers
    ]
    if len(selected) < 2:
        return PadstackInference(
            slot.id,
            None,
            ("SLOT_PADSTACK_NEEDS_MULTILAYER_EVIDENCE",),
        )

    cx, cy = desc["center"]
    centers = [(pad.center.x, pad.center.y) for pad in selected]
    if any(hypot(x - cx, y - cy) > tolerance_mm for x, y in centers):
        return PadstackInference(slot.id, None, ("SLOT_PAD_CENTER_MISMATCH",))

    shapes = {str(pad.shape).upper() for pad in selected}
    if len(shapes) != 1:
        return PadstackInference(slot.id, None, ("SLOT_PAD_SHAPE_CONFLICT",))

    sx0, sy0 = float(selected[0].size_x), float(selected[0].size_y)
    if any(
        not (
            _near(pad.size_x, sx0, tolerance_mm)
            and _near(pad.size_y, sy0, tolerance_mm)
        )
        for pad in selected[1:]
    ):
        return PadstackInference(slot.id, None, ("SLOT_PAD_SIZE_CONFLICT",))

    nets = {pad.net_id for pad in selected if pad.net_id is not None}
    if len(nets) > 1:
        return PadstackInference(slot.id, None, ("SLOT_PAD_NET_CONFLICT",))
    net_id = next(iter(nets)) if nets else None

    pad_size = (sx0, sy0) if orth == 0 else (sy0, sx0)
    layers = tuple(pad.layer for pad in selected)
    evidence = [
        "slot_plating_proven",
        "multilayer_copper_coverage",
        "uniform_pad_geometry",
    ]
    if declared_layers is not None:
        evidence.append("x2_declared_copper_coverage")
    if getattr(slot, "x2_layer_span", None) is not None:
        evidence.append("x2_proven_layer_span")

    padstack = PlatedSlotPadstack(
        slot.id,
        desc["center"],
        desc["angle_deg"],
        pad_size,
        str(selected[0].shape).upper(),
        (desc["long_mm"], desc["short_mm"]),
        layers,
        net_id,
        tuple(sorted(pad.id for pad in selected)),
        .95,
        tuple(evidence),
    )
    return PadstackInference(slot.id, padstack, ())
