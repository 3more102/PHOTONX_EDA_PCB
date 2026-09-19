import pytest

from photonx_eda_pcb.spatial_connectivity import AABB, SpatialHashIndex
from photonx_eda_pcb.spatial_connectivity.native_backend import (
    NativeBackendUnsupported,
    native_available,
)
from photonx_eda_pcb.spatial_connectivity.points import (
    batch_radius_query,
    radius_query,
)


def _point_index():
    index = SpatialHashIndex(0.5)
    index.insert("z", AABB(-1.0, 0.0, -1.0, 0.0))
    index.insert("a", AABB(1.0, 0.0, 1.0, 0.0))
    index.insert("center", AABB(0.0, 0.0, 0.0, 0.0))
    index.insert("diag", AABB(0.9, 0.9, 0.9, 0.9))
    index.insert("far", AABB(3.0, 4.0, 3.0, 4.0))
    return index


def test_radius_query_keeps_python_reference_as_default():
    assert radius_query(_point_index(), 0.0, 0.0, 1.0) == [
        (0.0, "center"),
        (1.0, "a"),
        (1.0, "z"),
    ]


def test_batch_radius_query_python_matches_individual_queries():
    index = _point_index()
    queries = ((0.0, 0.0, 1.0), (3.0, 4.0, 0.0), (-1.0, 0.0, 0.0))
    assert batch_radius_query(index, queries) == [
        radius_query(index, *query) for query in queries
    ]


def test_radius_query_unknown_backend_is_rejected():
    with pytest.raises(ValueError, match="backend"):
        radius_query(_point_index(), 0.0, 0.0, 1.0, backend="gpu")


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_native_batch_radius_query_matches_python_and_filters_square_false_positives():
    index = _point_index()
    queries = (
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 1.0),
        (-0.25, 0.0, 1.25),
        (3.0, 4.0, 5.0),
    )
    assert batch_radius_query(index, queries, backend="native") == batch_radius_query(
        index, queries, backend="python"
    )
    assert "diag" not in [
        oid for _, oid in radius_query(index, 0.0, 0.0, 1.0, backend="native")
    ]


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_native_radius_query_preserves_distance_then_id_tie_order():
    assert radius_query(_point_index(), 0.0, 0.0, 1.0, backend="native") == [
        (0.0, "center"),
        (1.0, "a"),
        (1.0, "z"),
    ]


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_native_radius_query_rejects_negative_radius_when_forced():
    with pytest.raises(NativeBackendUnsupported):
        radius_query(_point_index(), 0.0, 0.0, -1.0, backend="native")
