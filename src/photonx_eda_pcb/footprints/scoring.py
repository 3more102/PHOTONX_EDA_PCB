def _count_matches(features, signature):
    count = features["count"]
    if "pad_count" in signature and count != signature["pad_count"]:
        return False
    if count < signature.get("pad_count_min", count):
        return False
    if count > signature.get("pad_count_max", count):
        return False
    if signature.get("pad_count_even") and count % 2:
        return False
    return True


def score_signature(features, sig):
    if not _count_matches(features, sig):
        return 0.0

    score = float(sig.get("base_score", 0.35))
    if "pad_count" in sig:
        score += 0.10

    drilled = features["drilled_fraction"]
    if "drilled_min" in sig:
        if drilled < sig["drilled_min"]:
            return 0.0
        score += 0.20
    if "drilled_max" in sig:
        if drilled > sig["drilled_max"]:
            return 0.0
        score += 0.20

    if "row_count" in sig:
        if features.get("row_count") != sig["row_count"]:
            return 0.0
        score += 0.20

    if "row_size" in sig:
        row_sizes = features.get("row_sizes", ())
        if not row_sizes or any(size != sig["row_size"] for size in row_sizes):
            return 0.0
        score += 0.10

    if "row_balance_min" in sig:
        if features.get("row_balance", 0.0) < sig["row_balance_min"]:
            return 0.0
        score += 0.10

    if "pitch_cv_max" in sig:
        pitch_cv = features.get("pitch_cv")
        if pitch_cv is None or pitch_cv > sig["pitch_cv_max"]:
            return 0.0
        score += 0.10

    grid_rows, grid_columns = features.get("grid_shape", (0, 0))
    if "grid_rows_min" in sig:
        if grid_rows < sig["grid_rows_min"]:
            return 0.0
        score += 0.10
    if "grid_columns_min" in sig:
        if grid_columns < sig["grid_columns_min"]:
            return 0.0
        score += 0.10

    if "grid_occupancy_min" in sig:
        if features.get("grid_occupancy", 0.0) < sig["grid_occupancy_min"]:
            return 0.0
        score += 0.10

    if "symmetry_min" in sig:
        if features.get("symmetry_score", 0.0) < sig["symmetry_min"]:
            return 0.0
        score += 0.10

    pitch_min = features.get("pitch_min")
    if "pitch_min_mm" in sig:
        if pitch_min is None or pitch_min < sig["pitch_min_mm"]:
            return 0.0
        score += 0.05
    if "pitch_max_mm" in sig:
        if pitch_min is None or pitch_min > sig["pitch_max_mm"]:
            return 0.0
        score += 0.05

    # Preserve support for custom/legacy signature definitions.
    if "aspect_min" in sig:
        if features.get("aspect", 0.0) < sig["aspect_min"]:
            return 0.0
        score += 0.05

    return max(0.0, min(1.0, score))
