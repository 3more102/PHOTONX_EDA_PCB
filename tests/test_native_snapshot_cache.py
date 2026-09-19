import gc
import weakref

from photonx_eda_pcb.spatial_connectivity import AABB, SpatialHashIndex
from photonx_eda_pcb.spatial_connectivity import native_backend


def test_spatial_index_revision_advances_on_insert():
    index = SpatialHashIndex(1.0)
    assert index.revision == 0

    index.insert("a", AABB(0.0, 0.0, 0.0, 0.0))
    assert index.revision == 1

    index.insert("b", AABB(1.0, 1.0, 1.0, 1.0))
    assert index.revision == 2


def test_native_index_snapshot_is_reused_until_index_changes():
    native_backend._clear_index_snapshot_cache()
    index = SpatialHashIndex(1.0)
    index.insert("a", AABB(0.0, 0.0, 0.0, 0.0))

    first = native_backend._native_index_snapshot(index)
    second = native_backend._native_index_snapshot(index)

    assert second is first
    assert first.ids == ("a",)

    index.insert("b", AABB(1.0, 1.0, 1.0, 1.0))
    third = native_backend._native_index_snapshot(index)

    assert third is not first
    assert third.revision == index.revision
    assert third.ids == ("a", "b")


def test_native_snapshot_cache_does_not_keep_indexes_alive():
    native_backend._clear_index_snapshot_cache()
    index = SpatialHashIndex(1.0)
    index.insert("a", AABB(0.0, 0.0, 0.0, 0.0))
    native_backend._native_index_snapshot(index)

    reference = weakref.ref(index)
    del index
    gc.collect()

    assert reference() is None
