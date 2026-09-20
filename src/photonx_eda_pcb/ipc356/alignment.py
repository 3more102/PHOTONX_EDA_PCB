from dataclasses import dataclass, replace
from math import hypot, isfinite, sqrt


@dataclass(frozen=True)
class Ipc356TranslationAlignment:
    dx_mm: float
    dy_mm: float
    matched_records: int
    total_records: int
    rms_residual_mm: float
    max_residual_mm: float


def _record_points(records):
    out = []
    for index, record in enumerate(records):
        x = getattr(record, "x", None)
        y = getattr(record, "y", None)
        if x is None or y is None:
            continue
        x = float(x)
        y = float(y)
        if not isfinite(x) or not isfinite(y):
            continue
        out.append((index, record, x, y))
    return out


def _pad_points(pads):
    out = []
    for index, pad in enumerate(pads):
        center = getattr(pad, "center", None)
        if center is None:
            continue
        try:
            x = float(center.x)
            y = float(center.y)
        except (AttributeError, TypeError, ValueError):
            continue
        if not isfinite(x) or not isfinite(y):
            continue
        out.append((index, pad, x, y, str(getattr(pad, "id", index))))
    return out


def _score_translation(record_points, pad_points, dx, dy, tolerance_mm):
    edges = []
    for record_index, _record, x, y in record_points:
        tx = x + dx
        ty = y + dy
        for pad_index, _pad, px, py, pad_id in pad_points:
            distance = hypot(px - tx, py - ty)
            if distance <= tolerance_mm:
                edges.append((distance, record_index, pad_id, pad_index))

    used_records = set()
    used_pads = set()
    residuals = []
    for distance, record_index, _pad_id, pad_index in sorted(edges):
        if record_index in used_records or pad_index in used_pads:
            continue
        used_records.add(record_index)
        used_pads.add(pad_index)
        residuals.append(distance)

    if not residuals:
        return 0, float("inf"), float("inf")
    sum_sq = sum(value * value for value in residuals)
    rms = sqrt(sum_sq / len(residuals))
    return len(residuals), rms, max(residuals)


def infer_translation_alignment(
    records,
    pads,
    tolerance_mm=0.15,
    *,
    min_matches=2,
    ambiguity_margin_mm=None,
    max_pair_candidates=250000,
    max_scored_candidates=64,
):
    tolerance_mm = float(tolerance_mm)
    if not isfinite(tolerance_mm) or tolerance_mm <= 0:
        raise ValueError("tolerance_mm must be a positive finite number")
    min_matches = int(min_matches)
    if min_matches < 2:
        raise ValueError("min_matches must be at least 2")
    max_pair_candidates = int(max_pair_candidates)
    max_scored_candidates = int(max_scored_candidates)
    if max_pair_candidates <= 0 or max_scored_candidates <= 0:
        raise ValueError("candidate limits must be positive")

    record_points = _record_points(records)
    pad_points = _pad_points(pads)
    if len(record_points) < min_matches or len(pad_points) < min_matches:
        return None

    pair_count = len(record_points) * len(pad_points)
    if pair_count > max_pair_candidates:
        return None

    bucket_size = max(tolerance_mm / 2.0, 1e-9)
    buckets = {}
    for _ri, _record, rx, ry in record_points:
        for _pi, _pad, px, py, _pad_id in pad_points:
            dx = px - rx
            dy = py - ry
            key = (round(dx / bucket_size), round(dy / bucket_size))
            buckets.setdefault(key, []).append((dx, dy))

    ranked_buckets = sorted(
        buckets.items(),
        key=lambda item: (-len(item[1]), item[0][0], item[0][1]),
    )[:max_scored_candidates]

    candidates = []
    for key, offsets in ranked_buckets:
        ordered_dx = sorted(value[0] for value in offsets)
        ordered_dy = sorted(value[1] for value in offsets)
        mid = len(offsets) // 2
        if len(offsets) % 2:
            dx = ordered_dx[mid]
            dy = ordered_dy[mid]
        else:
            dx = (ordered_dx[mid - 1] + ordered_dx[mid]) / 2.0
            dy = (ordered_dy[mid - 1] + ordered_dy[mid]) / 2.0
        matched, rms, max_residual = _score_translation(
            record_points, pad_points, dx, dy, tolerance_mm
        )
        candidates.append((matched, rms, max_residual, dx, dy, key))

    candidates.sort(
        key=lambda item: (
            -item[0],
            item[1],
            item[2],
            abs(item[3]) + abs(item[4]),
            item[3],
            item[4],
            item[5],
        )
    )
    if not candidates or candidates[0][0] < min_matches:
        return None

    best = candidates[0]
    if ambiguity_margin_mm is None:
        ambiguity_margin_mm = tolerance_mm / 10.0
    ambiguity_margin_mm = float(ambiguity_margin_mm)
    if not isfinite(ambiguity_margin_mm) or ambiguity_margin_mm < 0:
        raise ValueError("ambiguity_margin_mm must be finite and non-negative")

    for other in candidates[1:]:
        if other[0] != best[0]:
            break
        distinct_translation = (
            abs(other[3] - best[3]) > 1e-12 or abs(other[4] - best[4]) > 1e-12
        )
        if distinct_translation and other[1] <= best[1] + ambiguity_margin_mm:
            return None

    return Ipc356TranslationAlignment(
        dx_mm=round(best[3], 12),
        dy_mm=round(best[4], 12),
        matched_records=best[0],
        total_records=len(record_points),
        rms_residual_mm=round(best[1], 12),
        max_residual_mm=round(best[2], 12),
    )


def translate_records(records, alignment):
    dx = float(alignment.dx_mm)
    dy = float(alignment.dy_mm)
    out = []
    for record in records:
        x = getattr(record, "x", None)
        y = getattr(record, "y", None)
        if x is None or y is None:
            out.append(record)
            continue
        out.append(replace(record, x=float(x) + dx, y=float(y) + dy))
    return out
