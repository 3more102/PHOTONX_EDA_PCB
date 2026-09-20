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
    for major, minor in sorted(points, key=lambda item: (item[1], item[0])):
        if not rows or abs(minor - rows[-1]["mean"]) > tolerance:
            rows.append({"mean": minor, "points": [(major, minor)]})
            continue

        row = rows[-1]
        row["points"].append((major, minor))
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
    major_values = [major for major, _ in points]
    minor_values = [minor for _, minor in points]
    span_major = max(major_values) - min(major_values)
    span_minor = max(minor_values) - min(minor_values)
    if span_minor > span_major:
        points = [(minor, major) for major, minor in points]
        span_major, span_minor = span_minor, span_major

    tolerance = max(1e-6, (pitch_min or max(span_major, 1.0)) * 0.20)
    rows = _cluster_rows(points, tolerance)
    row_sizes = tuple(len(row["points"]) for row in rows)

    pitch_steps = []
    for row in rows:
        ordered = sorted(major for major, _ in row["points"])
        pitch_steps.extend(
            b - a
            for a, b in zip(ordered, ordered[1:])
            if b - a > 1e-9
        )

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
        "pitch_cv": _coefficient_of_variation(pitch_steps),
    }
