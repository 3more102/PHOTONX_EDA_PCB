from .native_backend import (
    NativeBackendUnavailable,
    NativeBackendUnsupported,
    native_aabb_queries,
)


def aabb_queries(index, queries, backend="auto"):
    query_boxes = tuple(queries)
    selected = str(backend).lower()
    if selected not in {"auto", "python", "native"}:
        raise ValueError("backend must be 'auto', 'python', or 'native'")

    if selected != "python":
        try:
            return native_aabb_queries(index, query_boxes)
        except (NativeBackendUnavailable, NativeBackendUnsupported):
            if selected == "native":
                raise

    return [index.query(box) for box in query_boxes]
