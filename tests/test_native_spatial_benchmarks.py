import pytest

from photonx_eda_pcb.benchmark_comparisons.native_spatial import (
    benchmark_candidate_pair_backends,
    benchmark_radius_query_backends,
    native_backend_summary,
)
from photonx_eda_pcb.spatial_connectivity import AABB, SpatialHashIndex
from photonx_eda_pcb.spatial_connectivity.native_backend import native_available


def _index(count=120):
    index = SpatialHashIndex(0.5)
    for i in range(count):
        row, col = divmod(i, 15)
        x = col * 0.27 - 1.5
        y = row * 0.23 - 0.8
        index.insert(
            f"id-{count - i:04d}",
            AABB(x, y, x + 0.09, y + 0.07),
        )
    return index


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_candidate_pair_benchmark_checks_parity_without_timing_claim():
    reference, native = benchmark_candidate_pair_backends(
        _index(),
        0.2,
        iterations=1,
        warmup=0,
    )

    assert reference.samples[0].result_size == native.samples[0].result_size
    summary = native_backend_summary(reference, native)
    assert summary["python_samples"] == 1
    assert summary["native_samples"] == 1
    assert summary["python_median_seconds"] >= 0.0
    assert summary["native_median_seconds"] >= 0.0


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_radius_benchmark_checks_batched_result_parity():
    index = _index()
    queries = tuple(
        ((i % 12) * 0.19 - 1.0, (i // 12) * 0.17 - 0.5, 0.31)
        for i in range(48)
    )
    reference, native = benchmark_radius_query_backends(
        index,
        queries,
        iterations=1,
        warmup=0,
    )

    assert reference.samples[0].result_size == len(queries)
    assert native.samples[0].result_size == len(queries)
    summary = native_backend_summary(reference, native)
    assert summary["native_to_python_ratio"] is None or (
        summary["native_to_python_ratio"] >= 0.0
    )
