from .native_backend import (
    NativeBackendUnavailable,
    NativeBackendUnsupported,
    native_candidate_pairs,
)


def _candidate_pairs_python(index, tolerance=0.0):
    out = set()
    for oid in index.ids():
        q = index.query(index.box(oid).expanded(tolerance))
        for other in q:
            if other == oid:
                continue
            out.add(tuple(sorted((oid, other))))
    return sorted(out)


def candidate_pairs(index, tolerance=0.0, backend="auto"):
    selected = str(backend).lower()
    if selected not in {"auto", "python", "native"}:
        raise ValueError("backend must be 'auto', 'python', or 'native'")

    if selected != "python":
        try:
            return native_candidate_pairs(index, tolerance)
        except (NativeBackendUnavailable, NativeBackendUnsupported):
            if selected == "native":
                raise

    return _candidate_pairs_python(index, tolerance)
