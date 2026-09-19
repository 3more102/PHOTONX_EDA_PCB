import pytest

from photonx_eda_pcb.spatial_connectivity import AABB, SpatialHashIndex
from photonx_eda_pcb.spatial_connectivity.native_backend import (
    NativeBackendUnsupported,
    native_available,
)
from photonx_eda_pcb.spatial_connectivity.points import radius_query, radius_queries


def _point_index():
    index = SpatialHashIndex(0.5)
    for obj_id, x, y in [
        ("z", -1.0, -1.0),
        ("a", 0.0, 0.0),
        ("b", 0.3, 0.4),
        ("c", 0.5, 0.0),
        ("d", 1.2, 0.0),
    ]:
        index.insert(obj_id, AABB(x, y, x, y))
    return index


def test_batch_radius_python_matches_single_query_reference():
    index = _point_index()
    queries = [(0.0, 0.0), (-1.0, -1.0), (0.6, 0.0)]

    expected = [radius_query(index, x, y, 0.5) for x, y in queries]

    assert radius_queries(index, queries, 0.5, backend="python") == expected
    assert radius_queries(index, queries, 0.5, backend="auto") == expected


def test_batch_radius_rejects_unknown_backend():
    with pytest.raises(ValueError, match="backend"):
        radius_queries(_point_index(), [(0.0, 0.0)], 1.0, backend="gpu")


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_batch_radius_matches_python_reference():
    index = SpatialHashIndex(0.37)
    for i in range(160):
        row, col = divmod(i, 20)
        x = col * 0.19 - 1.7
        y = row * 0.23 - 0.8
        index.insert(f"id-{159 - i:03d}", AABB(x, y, x, y))

    queries = [
        (-1.7, -0.8),
        (-0.95, -0.11),
        (0.0, 0.0),
        (1.42, 0.81),
    ]

    for radius in (0.0, 0.05, 0.25, 0.75):
        assert radius_queries(index, queries, radius, backend="native") == radius_queries(
            index, queries, radius, backend="python"
        )


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_batch_radius_preserves_distance_then_id_tie_breaking():
    index = SpatialHashIndex(1.0)
    index.insert("z", AABB(-1.0, 0.0, -1.0, 0.0))
    index.insert("a", AABB(1.0, 0.0, 1.0, 0.0))
    index.insert("m", AABB(0.0, 1.0, 0.0, 1.0))

    assert radius_queries(index, [(0.0, 0.0)], 1.0, backend="native") == [
        [(1.0, "a"), (1.0, "m"), (1.0, "z")]
    ]


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_batch_radius_negative_radius_stays_on_python_reference_path():
    index = _point_index()

    assert radius_queries(index, [(0.0, 0.0)], -0.1, backend="auto") == [[]]
    with pytest.raises(NativeBackendUnsupported):
        radius_queries(index, [(0.0, 0.0)], -0.1, backend="native")
