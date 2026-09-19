def compare_metrics(expected, observed, tolerances=None, unknowns=()):
    """Compare observed metrics while preserving explicitly unknown fields.

    Keys declared in unknowns are intentionally outside the assertion boundary.
    They are ignored whether present or absent in observed. Every other
    unexpected, missing, or mismatched key remains a failure.
    """

    tolerances = tolerances or {}
    ignored = set(unknowns or ())
    differences = []

    keys = (set(expected) | set(observed)) - ignored
    for key in sorted(keys):
        if key not in expected:
            differences.append(("unexpected", key, None, observed[key]))
            continue
        if key not in observed:
            differences.append(("missing", key, expected[key], None))
            continue

        expected_value = expected[key]
        observed_value = observed[key]
        tolerance = tolerances.get(key)
        if (
            tolerance is not None
            and isinstance(expected_value, (int, float))
            and isinstance(observed_value, (int, float))
        ):
            if abs(float(expected_value) - float(observed_value)) > float(tolerance):
                differences.append(
                    ("mismatch", key, expected_value, observed_value)
                )
        elif expected_value != observed_value:
            differences.append(("mismatch", key, expected_value, observed_value))

    return differences
