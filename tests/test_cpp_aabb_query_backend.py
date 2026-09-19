import pytest

from photonx_eda_pcb.spatial_connectivity import AABB, SpatialHashIndex, aabb_queries
from photonx_eda_pcb.spatial_connectivity import queries as query_module
from photonx_eda_pcb.spatial_connectivity.native_backend import (
    NativeBackendUnsupported,
    native_available,
)


def _index():
    index = SpatialHashIndex(0.5)
    index.insert("z-neg", AABB(-2.0, -1.5, -0.5, -0.5))
    index.insert("a-origin", AABB(0.0, 0.0, 1.0, 1.0))
    index.insert("m-wide", AABB(0.5, 0.5, 2.1, 1.6))
    index.insert("q-far", AABB(4.0, 4.0, 4.2, 4.2))
    return index


def test_aabb_queries_python_contract_and_inclusive_boundaries():
    index = _index()
    boxes = (
        AABB(-0.5, -0.5, 0.0, 0.0),
        AABB(0.75, 0.75, 0.8, 0.8),
        AABB(10.0, 10.0, 11.0, 11.0),
    )

    assert aabb_queries(index, boxes, backend="python") == [
        ["a-origin", "z-neg"],
        ["a-origin", "m-wide"],
        [],
    ]


def test_aabb_queries_rejects_unknown_backend():
    with pytest.raises(ValueError, match="backend"):
        aabb_queries(_index(), (), backend="gpu")


def test_aabb_queries_auto_falls_back_for_unsupported_native_input(monkeypatch):
    index = _index()
    boxes = (AABB(0.0, 0.0, 0.5, 0.5),)
    expected = aabb_queries(index, boxes, backend="python")

    def unsupported(*_args, **_kwargs):
        raise NativeBackendUnsupported("simulated unsupported range")

    monkeypatch.setattr(query_module, "native_aabb_queries", unsupported)
    assert aabb_queries(index, boxes, backend="auto") == expected


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_aabb_batch_matches_python_reference_and_deduplicates_cells():
    index = SpatialHashIndex(0.25)
    for i in range(96):
        row, col = divmod(i, 12)
        x = col * 0.21 - 1.3
        y = row * 0.19 - 0.8
        width = 0.08 + (i % 5) * 0.07
        height = 0.06 + (i % 4) * 0.08
        index.insert(
            f"id-{95 - i:03d}",
            AABB(x, y, x + width, y + height),
        )

    boxes = (
        AABB(-1.3, -0.8, -1.3, -0.8),
        AABB(-0.5, -0.3, 0.7, 0.9),
        AABB(0.0, 0.0, 2.0, 2.0),
        AABB(8.0, 8.0, 8.1, 8.1),
    )

    native = aabb_queries(index, boxes, backend="native")
    python = aabb_queries(index, boxes, backend="python")
    assert native == python
    assert all(len(matches) == len(set(matches)) for matches in native)


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_aabb_batch_handles_empty_queries():
    assert aabb_queries(_index(), (), backend="native") == []


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_aabb_batch_native_mode_rejects_invalid_bounds():
    with pytest.raises(NativeBackendUnsupported):
        aabb_queries(
            _index(),
            (AABB(2.0, 2.0, 1.0, 1.0),),
            backend="native",
        )
