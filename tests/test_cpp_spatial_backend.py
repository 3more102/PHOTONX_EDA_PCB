import pytest

from photonx_eda_pcb.spatial_connectivity import AABB, SpatialHashIndex, candidate_pairs
from photonx_eda_pcb.spatial_connectivity import native_backend
from photonx_eda_pcb.spatial_connectivity.native_backend import (
    NativeBackendLoadError,
    native_available,
)


def _sample_index():
    index = SpatialHashIndex(0.75)
    entries = [
        ("z", AABB(-2.0, -1.0, -1.4, -0.2)),
        ("a", AABB(-1.35, -0.8, -0.9, -0.1)),
        ("m", AABB(0.0, 0.0, 0.5, 0.5)),
        ("b", AABB(0.58, 0.0, 1.0, 0.4)),
        ("q", AABB(3.0, 3.0, 3.2, 3.2)),
    ]
    for obj_id, box in reversed(entries):
        index.insert(obj_id, box)
    return index


def test_backend_selector_preserves_reference_contract():
    index = _sample_index()
    expected = candidate_pairs(index, 0.1, backend="python")
    assert expected == [("a", "z"), ("b", "m")]
    assert candidate_pairs(index, 0.1, backend="auto") == expected


def test_unknown_backend_is_rejected():
    with pytest.raises(ValueError, match="backend"):
        candidate_pairs(_sample_index(), backend="gpu")


def test_broken_native_library_does_not_silently_fallback(monkeypatch):
    index = _sample_index()
    native_backend._load_library.cache_clear()
    monkeypatch.setattr(
        native_backend,
        "_library_candidates",
        lambda: ("broken-photonx-native.so",),
    )

    def fail_load(_candidate):
        raise OSError("simulated loader failure")

    monkeypatch.setattr(native_backend.ctypes, "CDLL", fail_load)
    try:
        with pytest.raises(NativeBackendLoadError, match="simulated loader failure"):
            candidate_pairs(index, 0.1, backend="auto")
    finally:
        native_backend._load_library.cache_clear()


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_backend_matches_python_reference_across_tolerances():
    index = SpatialHashIndex(0.4)
    for i in range(120):
        row, col = divmod(i, 15)
        x = col * 0.31 - 2.0
        y = row * 0.29 - 1.0
        width = 0.08 + (i % 4) * 0.015
        height = 0.07 + (i % 5) * 0.01
        index.insert(
            f"id-{119 - i:03d}",
            AABB(x, y, x + width, y + height),
        )

    for tolerance in (0.0, 0.02, 0.08, 0.2):
        assert candidate_pairs(index, tolerance, backend="native") == candidate_pairs(
            index, tolerance, backend="python"
        )


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_backend_handles_touching_boundaries_and_negative_coordinates():
    index = SpatialHashIndex(1.0)
    index.insert("left", AABB(-2.0, -0.5, -1.0, 0.5))
    index.insert("touch", AABB(-1.0, -0.1, 0.0, 0.1))
    index.insert("gap", AABB(0.05, -0.1, 0.2, 0.1))

    assert candidate_pairs(index, backend="native") == [("left", "touch")]
    assert candidate_pairs(index, 0.05, backend="native") == [
        ("gap", "touch"),
        ("left", "touch"),
    ]
