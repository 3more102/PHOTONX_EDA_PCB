from types import SimpleNamespace

import pytest
from shapely.geometry import box

import photonx_eda_pcb.connectivity.spatial as spatial
import photonx_eda_pcb.native_backend as native_backend


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
