from math import hypot, isfinite

from photonx_eda_pcb.reference_designators.normalize import normalize_reference


def _nonnegative_finite(value, name):
    value = float(value)
    if not isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be a finite non-negative number")
    return value


def _validated_center(center):
    try:
        x, y = float(center[0]), float(center[1])
    except (TypeError, ValueError, IndexError) as exc:
        raise ValueError("center must contain two finite coordinates") from exc
    if not (isfinite(x) and isfinite(y)):
        raise ValueError("center must contain two finite coordinates")
    return x, y


def reference_candidates(silk_tokens, center, max_distance_mm=5.0, *, layer=None):
    """Return normalized reference-designator candidates ordered by distance.

    Invalid/non-reference text and tokens with non-finite coordinates are ignored.
    Duplicate observations of the same reference collapse to the nearest token.
    When layer is provided, only tokens from that exact silkscreen layer are
    considered.
    """
    cx, cy = _validated_center(center)
    limit = _nonnegative_finite(max_distance_mm, "max_distance_mm")
    nearest_by_reference = {}

    for token in silk_tokens:
        if layer is not None and getattr(token, "layer", None) != layer:
            continue

        reference = normalize_reference(getattr(token, "text", ""))
        if not reference:
            continue

        try:
            tx = float(getattr(token, "x"))
            ty = float(getattr(token, "y"))
        except (TypeError, ValueError, AttributeError):
            continue
        if not (isfinite(tx) and isfinite(ty)):
            continue

        distance = hypot(tx - cx, ty - cy)
        if distance > limit:
            continue

        previous = nearest_by_reference.get(reference)
        if previous is None or distance < previous:
            nearest_by_reference[reference] = distance

    return tuple(
        sorted(nearest_by_reference.items(), key=lambda item: (item[1], item[0]))
    )


def match_reference(
    silk_tokens,
    center,
    max_distance_mm=5.0,
    *,
    layer=None,
    ambiguity_margin_mm=0.0,
):
    """Return the nearest evidence-safe reference designator or None.

    Matching is fail-closed when another distinct reference lies within
    ambiguity_margin_mm of the best candidate. The default margin of zero
    rejects exact-distance ties without imposing a board-specific heuristic.
    """
    ambiguity_margin = _nonnegative_finite(
        ambiguity_margin_mm, "ambiguity_margin_mm"
    )
    ranked = reference_candidates(
        silk_tokens,
        center,
        max_distance_mm=max_distance_mm,
        layer=layer,
    )
    if not ranked:
        return None

    best_reference, best_distance = ranked[0]
    if len(ranked) > 1:
        _other_reference, other_distance = ranked[1]
        if other_distance - best_distance <= ambiguity_margin + 1e-12:
            return None

    return best_reference
