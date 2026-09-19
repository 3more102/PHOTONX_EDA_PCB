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
    "total_track_length_mm": "STATS_NEGATIVE_TRACK_LENGTH",
    "route_length_mm": "STATS_NEGATIVE_ROUTE_LENGTH",
    "outline_length_mm": "STATS_NEGATIVE_OUTLINE_LENGTH",
}

_DIMENSION_ISSUES = {
    "board_width_mm": "STATS_NEGATIVE_BOARD_WIDTH",
    "board_height_mm": "STATS_NEGATIVE_BOARD_HEIGHT",
}


def validate_stats(stats):
    issues = []
    for name in _COUNT_FIELDS:
        if getattr(stats, name, 0) < 0:
            issues.append("STATS_NEGATIVE_" + name.upper())

    for name, code in _LENGTH_ISSUES.items():
        if getattr(stats, name, 0.0) < 0:
            issues.append(code)

    for name, code in _DIMENSION_ISSUES.items():
        value = getattr(stats, name, None)
        if value is not None and value < 0:
            issues.append(code)

    return issues
