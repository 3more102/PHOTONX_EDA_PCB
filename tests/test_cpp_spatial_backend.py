import pytest

from photonx_eda_pcb.spatial_connectivity import AABB, SpatialHashIndex, candidate_pairs
from photonx_eda_pcb.spatial_connectivity import native_backend
from photonx_eda_pcb.spatial_connectivity.points import radius_query, radius_queries
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

    attempts = 0

    def fail_load(_candidate):
        nonlocal attempts
        attempts += 1
        raise OSError("simulated loader failure")

    monkeypatch.setattr(native_backend.ctypes, "CDLL", fail_load)
    try:
        for _ in range(2):
            with pytest.raises(NativeBackendLoadError, match="simulated loader failure"):
                candidate_pairs(index, 0.1, backend="auto")
        assert attempts == 1
    finally:
        native_backend._load_library.cache_clear()


def test_missing_native_library_discovery_is_cached(monkeypatch):
    index = _sample_index()
    expected = candidate_pairs(index, 0.1, backend="python")
    calls = 0

    native_backend._load_library.cache_clear()
    native_backend._library_candidates.cache_clear()
    monkeypatch.delenv("PHOTONX_NATIVE_LIBRARY", raising=False)

    def fake_find_library(_name):
        nonlocal calls
        calls += 1
        return None

    monkeypatch.setattr(native_backend, "find_library", fake_find_library)
    try:
        assert candidate_pairs(index, 0.1, backend="auto") == expected
        assert candidate_pairs(index, 0.1, backend="auto") == expected
        assert calls == 1
    finally:
        native_backend._load_library.cache_clear()
        native_backend._library_candidates.cache_clear()


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

@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_backend_preserves_reverse_direction_float_boundary_parity():
    def box_for(i):
        row, col = divmod(i, 15)
        x = col * 0.31 - 2.0
        y = row * 0.29 - 1.0
        width = 0.08 + (i % 4) * 0.015
        height = 0.07 + (i % 5) * 0.01
        return AABB(x, y, x + width, y + height)

    index = SpatialHashIndex(0.4)
    index.insert("a-upper", box_for(117))
    index.insert("z-lower", box_for(102))

    expected = candidate_pairs(index, 0.2, backend="python")
    assert expected == [("a-upper", "z-lower")]
    assert candidate_pairs(index, 0.2, backend="native") == expected



@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_backend_matches_python_at_asymmetric_float_tolerance_boundary():
    left = -15.416470322060789
    right = -11.831664827535912
    tolerance = 3.5848054945248764

    index = SpatialHashIndex(1.0)
    index.insert("a", AABB(left, 0.0, left, 0.0))
    index.insert("b", AABB(right, 0.0, right, 0.0))

    expected = candidate_pairs(index, tolerance, backend="python")
    assert expected == [("a", "b")]
    assert candidate_pairs(index, tolerance, backend="native") == expected

def test_radius_query_backend_selector_preserves_reference_contract():
    index = SpatialHashIndex(0.5)
    index.insert("z", AABB(-1.0, 0.0, -1.0, 0.0))
    index.insert("a", AABB(0.0, 0.0, 0.0, 0.0))
    index.insert("m", AABB(0.3, 0.4, 0.3, 0.4))

    queries = ((0.0, 0.0, 0.5), (-1.0, 0.0, -0.1))
    expected = radius_queries(index, queries, backend="python")
    assert expected == [[(0.0, "a"), (0.5, "m")], []]
    assert radius_queries(index, queries, backend="auto") == expected
    assert radius_query(index, 0.0, 0.0, 0.5, backend="python") == expected[0]


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_radius_batch_matches_python_reference():
    index = SpatialHashIndex(0.35)
    for i in range(80):
        x = (i % 10) * 0.17 - 0.8
        y = (i // 10) * 0.19 - 0.6
        index.insert(
            f"p-{79 - i:03d}",
            AABB(x - 0.02, y - 0.01, x + 0.02, y + 0.01),
        )

    queries = (
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.2),
        (-0.31, 0.17, 0.55),
        (0.52, -0.25, 1.1),
        (0.0, 0.0, -0.1),
    )
    assert radius_queries(index, queries, backend="native") == radius_queries(
        index, queries, backend="python"
    )

@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_radius_batch_matches_python_when_center_arithmetic_overflows():
    index = SpatialHashIndex(1e308)
    index.insert("huge", AABB(1e308, 0.0, 1e308, 0.0))

    expected = radius_query(index, 1e308, 0.0, 0.0, backend="python")
    assert expected == []
    assert radius_query(index, 1e308, 0.0, 0.0, backend="native") == expected

@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_radius_batch_matches_python_center_rounding_at_cell_boundary():
    left = 5.355248460778839e-14
    right = 3.7354625578691625e-13
    center = (left + right) / 2.0

    index = SpatialHashIndex(center)
    index.insert("edge", AABB(left, 0.0, right, 0.0))

    expected = radius_queries(index, ((center, 0.0, 0.0),), backend="python")
    assert expected == [[(0.0, "edge")]]
    assert radius_queries(index, ((center, 0.0, 0.0),), backend="native") == expected



def test_spatial_index_revision_tracks_insertions():
    index = SpatialHashIndex(1.0)
    assert index.revision == 0
    index.insert("a", AABB(0.0, 0.0, 0.1, 0.1))
    assert index.revision == 1
    index.insert("b", AABB(0.1, 0.0, 0.2, 0.1))
    assert index.revision == 2


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_persistent_index_handle_is_reused_until_revision_changes():
    index = SpatialHashIndex(1.0)
    index.insert("a", AABB(0.0, 0.0, 0.1, 0.1))

    library = native_backend._load_library()
    first = native_backend._get_native_index(index, library)
    second = native_backend._get_native_index(index, library)
    assert second is first

    index.insert("b", AABB(0.1, 0.0, 0.2, 0.1))
    third = native_backend._get_native_index(index, library)
    assert third is not first
    assert third.ids == ("a", "b")


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_persistent_index_refreshes_results_after_mutation():
    index = SpatialHashIndex(1.0)
    index.insert("a", AABB(0.0, 0.0, 0.1, 0.1))

    assert candidate_pairs(index, backend="native") == []
    assert radius_query(index, 0.15, 0.05, 0.06, backend="native") == []

    index.insert("b", AABB(0.1, 0.0, 0.2, 0.1))

    assert candidate_pairs(index, backend="native") == [("a", "b")]
    assert radius_query(index, 0.15, 0.05, 0.06, backend="native") == [
        (0.0, "b")
    ]
