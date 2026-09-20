from math import atan2, cos, hypot, sin, sqrt


def _principal_coordinates(pads):
    xs = [p.center.x for p in pads]
    ys = [p.center.y for p in pads]
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    centered = [(x - cx, y - cy) for x, y in zip(xs, ys)]

    xx = sum(x * x for x, _ in centered)
    yy = sum(y * y for _, y in centered)
    xy = sum(x * y for x, y in centered)
    angle = 0.5 * atan2(2.0 * xy, xx - yy) if len(pads) > 1 else 0.0
    c = cos(angle)
    s = sin(angle)
    return [
        (x * c + y * s, -x * s + y * c)
        for x, y in centered
    ]


def _cluster_rows(points, tolerance):
    rows = []
    for along, across in sorted(points, key=lambda item: (item[1], item[0])):
        if not rows or abs(across - rows[-1]["mean"]) > tolerance:
            rows.append({"mean": across, "points": [(along, across)]})
            continue

        row = rows[-1]
        row["points"].append((along, across))
        row["mean"] = sum(value for _, value in row["points"]) / len(row["points"])
    return rows


def _coefficient_of_variation(values):
    if not values:
        return None
    mean = sum(values) / len(values)
    if mean <= 1e-12:
        return None
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return sqrt(variance) / mean


def _layout(points, tolerance):
    rows = _cluster_rows(points, tolerance)
    row_sizes = tuple(len(row["points"]) for row in rows)
    pitch_steps = []
    for row in rows:
        ordered = sorted(along for along, _ in row["points"])
        pitch_steps.extend(
            b - a
            for a, b in zip(ordered, ordered[1:])
            if b - a > 1e-9
        )

    along_values = [along for along, _ in points]
    across_values = [across for _, across in points]
    return {
        "rows": rows,
        "row_sizes": row_sizes,
        "pitch_steps": pitch_steps,
        "span_along": max(along_values) - min(along_values),
        "span_across": max(across_values) - min(across_values),
    }


def _select_row_layout(points, tolerance):
    layouts = [
        _layout(points, tolerance),
        _layout([(across, along) for along, across in points], tolerance),
    ]
    return min(
        enumerate(layouts),
        key=lambda item: (
            len(item[1]["rows"]),
            -max(item[1]["row_sizes"], default=0),
            item[0],
        ),
    )[1]


def extract_group_features(pads):
    pads = list(pads)
    if not pads:
        return {
            "count": 0,
            "bbox": (0, 0, 0, 0),
            "centroid": (0, 0),
            "drilled_fraction": 0.0,
            "pitch_min": None,
            "span_major": 0.0,
            "span_minor": 0.0,
            "aspect": 0.0,
            "row_count": 0,
            "row_sizes": (),
            "row_balance": 0.0,
            "row_spacing": None,
            "pitch_cv": None,
        }

    xs = [p.center.x for p in pads]
    ys = [p.center.y for p in pads]
    n = len(pads)
    distances = [
        hypot(a.center.x - b.center.x, a.center.y - b.center.y)
        for i, a in enumerate(pads)
        for b in pads[i + 1 :]
    ]
    positive_distances = [distance for distance in distances if distance > 1e-9]
    pitch_min = min(positive_distances) if positive_distances else None

    points = _principal_coordinates(pads)
    raw_spans = (
        max(along for along, _ in points) - min(along for along, _ in points),
        max(across for _, across in points) - min(across for _, across in points),
    )
    tolerance = max(1e-6, (pitch_min or max(raw_spans[0], raw_spans[1], 1.0)) * 0.20)
    layout = _select_row_layout(points, tolerance)
    rows = layout["rows"]
    row_sizes = layout["row_sizes"]
    span_along = layout["span_along"]
    span_across = layout["span_across"]
    span_major = max(span_along, span_across)
    span_minor = min(span_along, span_across)

    row_spacing = None
    if len(rows) == 2:
        row_spacing = abs(rows[1]["mean"] - rows[0]["mean"])

    row_balance = (
        min(row_sizes) / max(row_sizes)
        if row_sizes and max(row_sizes)
        else 0.0
    )
    aspect = (
        span_major / span_minor
        if span_minor > 1e-9
        else float("inf") if span_major > 1e-9 else 1.0
    )

    return {
        "count": n,
        "bbox": (min(xs), min(ys), max(xs), max(ys)),
        "centroid": (sum(xs) / n, sum(ys) / n),
        "drilled_fraction": sum(p.drill is not None for p in pads) / n,
        "pitch_min": pitch_min,
        "span_major": span_major,
        "span_minor": span_minor,
        "aspect": aspect,
        "row_count": len(rows),
        "row_sizes": row_sizes,
        "row_balance": row_balance,
        "row_spacing": row_spacing,
        "pitch_cv": _coefficient_of_variation(layout["pitch_steps"]),
    }
