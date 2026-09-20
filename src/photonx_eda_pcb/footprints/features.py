from math import atan2, cos, degrees, hypot, pi, sin

_EPS = 1e-12


def _lattice_angle(points):
    """Estimate a package lattice axis from the shortest pad-to-pad vectors.

    Angles that differ by 90 degrees are equivalent for rectangular package
    geometry, so the fourth angular moment gives a deterministic orientation
    for rotated rows and grids without requiring NumPy.
    """
    pairs = []
    for i, (x1, y1) in enumerate(points):
        for x2, y2 in points[i + 1 :]:
            dx, dy = x2 - x1, y2 - y1
            distance = hypot(dx, dy)
            if distance > _EPS:
                pairs.append((distance, atan2(dy, dx)))
    if not pairs:
        return 0.0

    pairs.sort(key=lambda item: (item[0], item[1]))
    nearest = pairs[0][0]
    near_angles = [
        angle for distance, angle in pairs if distance <= nearest * 1.25 + _EPS
    ]
    sx = sum(cos(4.0 * angle) for angle in near_angles)
    sy = sum(sin(4.0 * angle) for angle in near_angles)
    angle = near_angles[0] if abs(sx) + abs(sy) < _EPS else atan2(sy, sx) / 4.0

    while angle >= pi / 4.0:
        angle -= pi / 2.0
    while angle < -pi / 4.0:
        angle += pi / 2.0
    return angle


def _cluster_levels(values, tolerance):
    groups = []
    for value in sorted(values):
        if not groups:
            groups.append([value])
            continue
        center = sum(groups[-1]) / len(groups[-1])
        if abs(value - center) > tolerance:
            groups.append([value])
        else:
            groups[-1].append(value)
    return tuple((sum(group) / len(group), len(group)) for group in groups)


def _two_row_score(first, second, count):
    if len(first) != 2 or len(second) < 2:
        return 0.0
    sizes = [item[1] for item in first]
    balance = min(sizes) / max(sizes)
    occupancy = count / max(1, len(first) * len(second))
    return max(0.0, min(1.0, balance * min(1.0, occupancy)))


def _symmetry_score(points, cx, cy, tolerance):
    if not points:
        return 0.0
    matched = 0
    for x, y in points:
        target_x, target_y = 2.0 * cx - x, 2.0 * cy - y
        if min(hypot(target_x - px, target_y - py) for px, py in points) <= tolerance:
            matched += 1
    return matched / len(points)


def extract_group_features(pads):
    if not pads:
        return {
            "count": 0,
            "bbox": (0, 0, 0, 0),
            "centroid": (0, 0),
            "drilled_fraction": 0.0,
            "pitch_min": None,
            "lattice_angle_deg": 0.0,
            "grid_shape": (0, 0),
            "grid_occupancy": 0.0,
            "two_row_score": 0.0,
            "symmetry_score": 0.0,
        }

    points = [(p.center.x, p.center.y) for p in pads]
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    count = len(points)
    cx, cy = sum(xs) / count, sum(ys) / count

    distances = []
    positive_distances = []
    for i, first in enumerate(points):
        for second in points[i + 1 :]:
            distance = hypot(first[0] - second[0], first[1] - second[1])
            distances.append(distance)
            if distance > _EPS:
                positive_distances.append(distance)

    pitch_min = min(distances) if distances else None
    geometry_pitch = min(positive_distances) if positive_distances else None
    angle = _lattice_angle(points)
    c, s = cos(angle), sin(angle)
    rotated = [
        ((x - cx) * c + (y - cy) * s, -(x - cx) * s + (y - cy) * c)
        for x, y in points
    ]

    tolerance = max(1e-6, (geometry_pitch or 1.0) * 0.18)
    first_levels = _cluster_levels([u for u, _ in rotated], tolerance)
    second_levels = _cluster_levels([v for _, v in rotated], tolerance)
    rows, columns = sorted((len(first_levels), len(second_levels)))
    occupancy = (
        count / (len(first_levels) * len(second_levels))
        if first_levels and second_levels
        else 0.0
    )
    two_row = max(
        _two_row_score(first_levels, second_levels, count),
        _two_row_score(second_levels, first_levels, count),
    )
    symmetry = _symmetry_score(points, cx, cy, max(1e-6, tolerance * 1.5))

    return {
        "count": count,
        "bbox": (min(xs), min(ys), max(xs), max(ys)),
        "centroid": (cx, cy),
        "drilled_fraction": sum(
            getattr(p, "drill", None) is not None for p in pads
        )
        / count,
        "pitch_min": pitch_min,
        "lattice_angle_deg": degrees(angle),
        "grid_shape": (rows, columns),
        "grid_occupancy": round(max(0.0, min(1.0, occupancy)), 12),
        "two_row_score": round(two_row, 12),
        "symmetry_score": round(symmetry, 12),
    }
