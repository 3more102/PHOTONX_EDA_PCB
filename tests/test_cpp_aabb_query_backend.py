import pytest

from photonx_eda_pcb.spatial_connectivity import (
    AABB,
    SpatialHashIndex,
    aabb_queries,
)
from photonx_eda_pcb.spatial_connectivity.native_backend import native_available


def _index():
    index = SpatialHashIndex(0.5)
    index.insert("z-wide", AABB(-1.25, -0.75, 1.25, 0.75))
    index.insert("a-left", AABB(-2.0, -0.25, -1.25, 0.25))
    index.insert("m-right", AABB(1.25, -0.25, 1.8, 0.25))
    index.insert("q-far", AABB(4.0, 4.0, 4.2, 4.2))
    return index


def test_batch_aabb_python_matches_repeated_index_query():
    index = _index()
    queries = (
        AABB(-1.25, 0.0, -1.25, 0.0),
        AABB(1.25, 0.0, 1.25, 0.0),
        AABB(-0.6, -0.6, 0.6, 0.6),
        AABB(10.0, 10.0, 11.0, 11.0),
    )
    assert aabb_queries(index, queries, backend="python") == [
        index.query(query) for query in queries
    ]


def test_batch_aabb_unknown_backend_is_rejected():
    with pytest.raises(ValueError, match="backend"):
        aabb_queries(_index(), (AABB(0.0, 0.0, 0.0, 0.0),), backend="gpu")


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_native_batch_aabb_matches_python_for_touching_and_negative_coordinates():
    index = _index()
    queries = (
        AABB(-1.25, 0.0, -1.25, 0.0),
        AABB(1.25, 0.0, 1.25, 0.0),
        AABB(-2.5, -1.0, -1.9, 1.0),
        AABB(4.2, 4.2, 4.2, 4.2),
    )
    assert aabb_queries(index, queries, backend="native") == aabb_queries(
        index,
        queries,
        backend="python",
    )


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_native_batch_aabb_deduplicates_boxes_spanning_many_cells():
    index = SpatialHashIndex(0.25)
    index.insert("large", AABB(-2.0, -2.0, 2.0, 2.0))
    index.insert("small", AABB(0.1, 0.1, 0.2, 0.2))
    query = AABB(-1.5, -1.5, 1.5, 1.5)

    result = aabb_queries(index, (query,), backend="native")
    assert result == [["large", "small"]]
    assert result == aabb_queries(index, (query,), backend="python")
