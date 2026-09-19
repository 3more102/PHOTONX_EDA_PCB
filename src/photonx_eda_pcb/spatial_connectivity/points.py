from math import hypot

from .grid import SpatialHashIndex
from .model import AABB
from .native_backend import (
    NativeBackendUnavailable,
    NativeBackendUnsupported,
    native_point_radius_candidates,
)


def point_box(x, y, radius=0.0):
    r = max(0.0, float(radius))
    x = float(x)
    y = float(y)
    return AABB(x - r, y - r, x + r, y + r)


def build_point_index(items, xy_fn, cell_size=1.0):
    idx = SpatialHashIndex(cell_size)
    for obj_id, obj in items:
        x, y = xy_fn(obj)
        idx.insert(obj_id, point_box(x, y))
    return idx


def _exact_radius_matches(index, x, y, radius, candidate_ids):
    x = float(x)
    y = float(y)
    radius = float(radius)
    out = []
    for oid in candidate_ids:
        b = index.box(oid)
        cx = (b.min_x + b.max_x) / 2
        cy = (b.min_y + b.max_y) / 2
        d = hypot(x - cx, y - cy)
        if d <= radius:
            out.append((d, oid))
    return sorted(out, key=lambda item: (item[0], item[1]))


def _radius_query_python(index, x, y, radius):
    return _exact_radius_matches(
        index,
        x,
        y,
        radius,
        index.query(point_box(x, y, radius)),
    )


def batch_radius_query(index, queries, *, backend="python"):
    query_values = tuple(queries)
    selected = str(backend).lower()
    if selected not in {"auto", "python", "native"}:
        raise ValueError("backend must be 'auto', 'python', or 'native'")

    if selected != "python":
        try:
            candidates = native_point_radius_candidates(index, query_values)
        except (NativeBackendUnavailable, NativeBackendUnsupported):
            if selected == "native":
                raise
        else:
            return [
                _exact_radius_matches(index, x, y, radius, candidate_ids)
                for (x, y, radius), candidate_ids in zip(query_values, candidates)
            ]

    return [
        _radius_query_python(index, x, y, radius)
        for x, y, radius in query_values
    ]


def radius_query(index, x, y, radius, *, backend="python"):
    return batch_radius_query(
        index,
        ((x, y, radius),),
        backend=backend,
    )[0]
