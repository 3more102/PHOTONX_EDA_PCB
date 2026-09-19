from types import SimpleNamespace

import pytest
from shapely.geometry import box

import photonx_eda_pcb.connectivity.spatial as spatial
import photonx_eda_pcb.native_backend as native_backend
from photonx_eda_pcb.spatial_connectivity import AABB, SpatialHashIndex, candidate_pairs


def test_native_adapter_returns_none_when_extension_is_unavailable(monkeypatch):
    monkeypatch.setattr(native_backend, "_native", None)
    assert (
        native_backend.try_native_candidate_pairs(
            [("a", 0.0, 0.0, 1.0, 1.0)],
            0.03,
            1.0,
        )
        is None
    )


def test_layer_candidate_pairs_uses_native_backend_when_available(monkeypatch):
    objects = [
        SimpleNamespace(id="b", layer="F.Cu"),
        SimpleNamespace(id="a", layer="F.Cu"),
        SimpleNamespace(id="c", layer="B.Cu"),
    ]
    shapes = {
        "a": box(0.0, 0.0, 1.0, 1.0),
        "b": box(0.9, 0.9, 2.0, 2.0),
        "c": box(0.0, 0.0, 1.0, 1.0),
    }
    calls = []

    def fake_native(records, tolerance, cell_size):
        calls.append((records, tolerance, cell_size))
        if len(records) < 2:
            return []
        return [("a", "b")]

    monkeypatch.setattr(spatial, "try_native_candidate_pairs", fake_native)

    assert spatial.layer_candidate_pairs(objects, shapes, 0.03, 1.0) == [("a", "b")]
    assert len(calls) == 1
    assert calls[0][1:] == (0.03, 1.0)


def test_compiled_native_backend_matches_python_contract_when_installed():
    if not native_backend.rust_spatial_available():
        pytest.skip("optional Rust extension is not installed")

    records = [
        ("c", 5.0, 5.0, 6.0, 6.0),
        ("a", 0.0, 0.0, 0.2, 0.2),
        ("b", 0.25, 0.0, 0.4, 0.2),
    ]
    assert native_backend.try_native_candidate_pairs(records, 0.0, 1.0) == []
    assert native_backend.try_native_candidate_pairs(records, 0.1, 1.0) == [
        ("a", "b")
    ]


@pytest.mark.parametrize(
    ("tolerance", "cell_size"),
    [(0.0, 1.0), (0.03, 0.25), (0.1, 1.0)],
)
def test_compiled_native_backend_matches_python_spatial_hash(
    tolerance,
    cell_size,
):
    if not native_backend.rust_spatial_available():
        pytest.skip("optional Rust extension is not installed")

    records = [
        ("neg-a", -1.10, -0.20, -0.90, 0.20),
        ("neg-b", -0.86, -0.10, -0.60, 0.10),
        ("edge-a", 0.00, 0.00, 0.25, 0.25),
        ("edge-b", 0.25, 0.25, 0.50, 0.50),
        ("far", 3.00, 3.00, 3.20, 3.20),
    ]
    index = SpatialHashIndex(cell_size)
    for obj_id, min_x, min_y, max_x, max_y in records:
        index.insert(obj_id, AABB(min_x, min_y, max_x, max_y))

    expected = candidate_pairs(index, tolerance)
    actual = native_backend.try_native_candidate_pairs(
        records,
        tolerance,
        cell_size,
    )
    assert actual == expected
