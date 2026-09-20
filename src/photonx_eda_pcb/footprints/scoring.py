def _legacy_score(features, sig):
    if features["count"] != sig.get("pad_count"):
        return 0.0
    score = 0.55
    drilled = features["drilled_fraction"]
    if "drilled_min" in sig:
        score += 0.25 if drilled >= sig["drilled_min"] else -0.25
    if "drilled_max" in sig:
        score += 0.25 if drilled <= sig["drilled_max"] else -0.25
    x0, y0, x1, y1 = features["bbox"]
    width = max(x1 - x0, 1e-9)
    height = max(y1 - y0, 1e-9)
    aspect = max(width / height, height / width)
    if aspect >= sig.get("aspect_min", 1):
        score += 0.15
    return max(0.0, min(1.0, score))


def _in_count_range(features, sig):
    count = features["count"]
    if "pad_count" in sig and count != sig["pad_count"]:
        return False
    if count < sig.get("pad_count_min", count):
        return False
    if count > sig.get("pad_count_max", count):
        return False
    return True


def _geometry_score(features, sig):
    if not _in_count_range(features, sig):
        return 0.0

    drilled = features["drilled_fraction"]
    if "drilled_min" in sig and drilled < sig["drilled_min"]:
        return 0.0
    if "drilled_max" in sig and drilled > sig["drilled_max"]:
        return 0.0

    two_row = features.get("two_row_score", 0.0)
    if two_row < sig.get("two_row_min", 0.0):
        return 0.0

    rows, columns = features.get("grid_shape", (0, 0))
    if rows < sig.get("grid_rows_min", 0):
        return 0.0
    if columns < sig.get("grid_columns_min", 0):
        return 0.0

    occupancy = features.get("grid_occupancy", 0.0)
    if occupancy < sig.get("grid_occupancy_min", 0.0):
        return 0.0

    symmetry = features.get("symmetry_score", 0.0)
    if symmetry < sig.get("symmetry_min", 0.0):
        return 0.0

    score = 0.2
    score += 0.25 if "pad_count" in sig else 0.1
    if "drilled_min" in sig or "drilled_max" in sig:
        score += 0.15
    if "two_row_min" in sig:
        score += 0.2 * two_row
    if "grid_occupancy_min" in sig:
        score += 0.2 * occupancy
    if "symmetry_min" in sig:
        score += 0.1 * symmetry

    # Generic geometry families must remain below a valid exact signature.
    return max(0.0, min(0.79, score))


def score_signature(features, sig):
    geometry_keys = {
        "pad_count_min",
        "pad_count_max",
        "two_row_min",
        "grid_rows_min",
        "grid_columns_min",
        "grid_occupancy_min",
        "symmetry_min",
    }
    if not geometry_keys.intersection(sig):
        return _legacy_score(features, sig)
    return _geometry_score(features, sig)
