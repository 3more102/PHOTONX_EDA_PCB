from __future__ import annotations

from photonx_eda_pcb.performance_profiles import benchmark
from photonx_eda_pcb.spatial_connectivity import candidate_pairs
from photonx_eda_pcb.spatial_connectivity.points import radius_queries


def _assert_parity(reference, native, label: str) -> None:
    if reference != native:
        raise AssertionError(f"{label} native/Python parity check failed")


def benchmark_candidate_pair_backends(
    index,
    tolerance: float = 0.0,
    *,
    iterations: int = 3,
    warmup: int = 1,
):
    """Benchmark native and Python AABB broad phases after a parity check."""
    reference_fn = lambda: candidate_pairs(index, tolerance, backend="python")
    native_fn = lambda: candidate_pairs(index, tolerance, backend="native")

    _assert_parity(reference_fn(), native_fn(), "candidate_pairs")
    reference = benchmark(
        "candidate_pairs_python",
        reference_fn,
        iterations=iterations,
        warmup=warmup,
    )
    native = benchmark(
        "candidate_pairs_native",
        native_fn,
        iterations=iterations,
        warmup=warmup,
    )
    return reference, native


def benchmark_radius_query_backends(
    index,
    queries,
    *,
    iterations: int = 3,
    warmup: int = 1,
):
    """Benchmark batched radius queries after exact result parity is proven."""
    query_specs = tuple(
        (float(x), float(y), float(radius))
        for x, y, radius in queries
    )
    reference_fn = lambda: radius_queries(
        index,
        query_specs,
        backend="python",
    )
    native_fn = lambda: radius_queries(
        index,
        query_specs,
        backend="native",
    )

    _assert_parity(reference_fn(), native_fn(), "radius_queries")
    reference = benchmark(
        "radius_queries_python",
        reference_fn,
        iterations=iterations,
        warmup=warmup,
    )
    native = benchmark(
        "radius_queries_native",
        native_fn,
        iterations=iterations,
        warmup=warmup,
    )
    return reference, native


def native_backend_summary(reference, native) -> dict[str, float | int | None]:
    """Return measurements without declaring either backend universally faster."""
    ratio = (
        None
        if reference.median_seconds <= 0.0
        else native.median_seconds / reference.median_seconds
    )
    return {
        "python_median_seconds": reference.median_seconds,
        "native_median_seconds": native.median_seconds,
        "native_to_python_ratio": ratio,
        "python_samples": len(reference.samples),
        "native_samples": len(native.samples),
    }
