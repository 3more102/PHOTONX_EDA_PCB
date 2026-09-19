import pytest

from photonx_eda_pcb.benchmark_comparisons import spatial_native
from photonx_eda_pcb.performance_profiles.model import BenchmarkResult, BenchmarkSample
from photonx_eda_pcb.spatial_connectivity import AABB, SpatialHashIndex
from photonx_eda_pcb.spatial_connectivity.native_backend import (
    NativeBackendUnavailable,
    native_available,
)


def _index():
    index = SpatialHashIndex(0.5)
    index.insert("a", AABB(0.0, 0.0, 0.2, 0.2))
    index.insert("b", AABB(0.25, 0.0, 0.45, 0.2))
    index.insert("c", AABB(2.0, 2.0, 2.2, 2.2))
    return index


def test_native_spatial_benchmark_requires_available_backend(monkeypatch):
    monkeypatch.setattr(spatial_native, "native_available", lambda: False)
    with pytest.raises(NativeBackendUnavailable, match="not available"):
        spatial_native.benchmark_candidate_pair_backends(
            _index(), tolerance=0.1, iterations=1, warmup=0
        )


def test_candidate_backend_summary_reports_ratio_without_claiming_threshold():
    python_result = BenchmarkResult(
        "candidate_pairs_python",
        (BenchmarkSample(0.02, 1),),
        0.02,
        0.02,
        0.02,
    )
    native_result = BenchmarkResult(
        "candidate_pairs_native",
        (BenchmarkSample(0.01, 1),),
        0.01,
        0.01,
        0.01,
    )

    summary = spatial_native.candidate_backend_summary(
        python_result, native_result
    )
    assert summary == {
        "python_seconds": 0.02,
        "native_seconds": 0.01,
        "native_to_python_ratio": 0.5,
        "native_faster": True,
    }


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_native_spatial_benchmark_preserves_candidate_pair_parity():
    python_result, native_result = (
        spatial_native.benchmark_candidate_pair_backends(
            _index(), tolerance=0.1, iterations=1, warmup=0
        )
    )

    assert python_result.samples[0].result_size == 1
    assert native_result.samples[0].result_size == 1
