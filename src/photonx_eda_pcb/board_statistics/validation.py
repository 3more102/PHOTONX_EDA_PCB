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

_LENGTH_FIELDS = (
    "total_track_length_mm",
    "route_length_mm",
    "outline_length_mm",
)


def validate_stats(stats):
    issues = []
    for name in _COUNT_FIELDS:
        if getattr(stats, name, 0) < 0:
            issues.append("STATS_NEGATIVE_" + name.upper())

    for name in _LENGTH_FIELDS:
        if getattr(stats, name, 0.0) < 0:
            issues.append("STATS_NEGATIVE_" + name.upper().replace("_MM", ""))

    for name in ("board_width_mm", "board_height_mm"):
        value = getattr(stats, name, None)
        if value is not None and value < 0:
            issues.append("STATS_NEGATIVE_" + name.upper().replace("_MM", ""))

    return issues
