from math import isfinite


_COUNT_FIELDS = (
    "tracks",
    "pads",
    "drills",
    "outline_segments",
    "nets",
    "components",
    "slots",
    "routes",
    "regions",
    "diagnostics",
)

_LENGTH_ISSUES = {
    "total_track_length_mm": (
        "STATS_NEGATIVE_TRACK_LENGTH",
        "STATS_NONFINITE_TRACK_LENGTH",
    ),
    "route_length_mm": (
        "STATS_NEGATIVE_ROUTE_LENGTH",
        "STATS_NONFINITE_ROUTE_LENGTH",
    ),
    "outline_length_mm": (
        "STATS_NEGATIVE_OUTLINE_LENGTH",
        "STATS_NONFINITE_OUTLINE_LENGTH",
    ),
}

_DIMENSION_ISSUES = {
    "board_width_mm": (
        "STATS_NEGATIVE_BOARD_WIDTH",
        "STATS_NONFINITE_BOARD_WIDTH",
    ),
    "board_height_mm": (
        "STATS_NEGATIVE_BOARD_HEIGHT",
        "STATS_NONFINITE_BOARD_HEIGHT",
    ),
}


def validate_stats(stats):
    issues = []
    for name in _COUNT_FIELDS:
        if getattr(stats, name, 0) < 0:
            issues.append("STATS_NEGATIVE_" + name.upper())

    for name, (negative_code, nonfinite_code) in _LENGTH_ISSUES.items():
        value = float(getattr(stats, name, 0.0))
        if not isfinite(value):
            issues.append(nonfinite_code)
        elif value < 0:
            issues.append(negative_code)

    for name, (negative_code, nonfinite_code) in _DIMENSION_ISSUES.items():
        value = getattr(stats, name, None)
        if value is None:
            continue
        value = float(value)
        if not isfinite(value):
            issues.append(nonfinite_code)
        elif value < 0:
            issues.append(negative_code)

    return issues
