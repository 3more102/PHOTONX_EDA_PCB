import pytest

from photonx_eda_pcb.benchmark_comparisons import (
    benchmark_candidate_pair_backends,
    native_candidate_pair_summary,
)
from photonx_eda_pcb.performance_profiles import benchmark
from photonx_eda_pcb.spatial_connectivity import AABB, SpatialHashIndex
from photonx_eda_pcb.spatial_connectivity.native_backend import native_available


def _benchmark_index():
    index = SpatialHashIndex(0.5)
    for i in range(64):
        row, col = divmod(i, 8)
        x = col * 0.22
        y = row * 0.24
        index.insert(
            f"id-{63 - i:03d}",
            AABB(x, y, x + 0.12, y + 0.10),
        )
    return index


def test_native_candidate_pair_summary_reports_ratio_without_policy():
    python_result = benchmark("python", lambda: [1, 2, 3], iterations=1, warmup=0)
    native_result = benchmark("native", lambda: [1, 2, 3], iterations=1, warmup=0)

    summary = native_candidate_pair_summary(python_result, native_result)

    assert summary["pairs"] == 3
    assert summary["python_seconds"] >= 0
    assert summary["native_seconds"] >= 0
    assert summary["native_to_python_ratio"] is None or summary["native_to_python_ratio"] >= 0
    assert (
        summary["python_over_native_speedup"] is None
        or summary["python_over_native_speedup"] >= 0
    )


def test_native_candidate_pair_summary_rejects_result_size_mismatch():
    python_result = benchmark("python", lambda: [1, 2], iterations=1, warmup=0)
    native_result = benchmark("native", lambda: [1], iterations=1, warmup=0)

    with pytest.raises(ValueError, match="result sizes"):
        native_candidate_pair_summary(python_result, native_result)


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_candidate_pair_backend_benchmark_preserves_reference_result_size():
    python_result, native_result = benchmark_candidate_pair_backends(
        _benchmark_index(),
        0.08,
        iterations=1,
        warmup=0,
    )
    summary = native_candidate_pair_summary(python_result, native_result)

    assert summary["pairs"] == python_result.samples[0].result_size
    assert summary["pairs"] == native_result.samples[0].result_size
    assert summary["pairs"] > 0
