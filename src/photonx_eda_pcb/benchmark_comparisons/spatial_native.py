from photonx_eda_pcb.performance_profiles import benchmark
from photonx_eda_pcb.spatial_connectivity import candidate_pairs
from photonx_eda_pcb.spatial_connectivity.native_backend import (
    NativeBackendUnavailable,
    native_available,
)
from photonx_eda_pcb.spatial_connectivity.points import radius_queries


def _require_native() -> None:
    if not native_available():
        raise NativeBackendUnavailable("native spatial backend is not available")


def _require_parity(reference, native, workload: str) -> None:
    if native != reference:
        raise AssertionError(
            f"native {workload} backend diverged from the Python reference"
        )


def benchmark_candidate_pair_backends(
    index,
    tolerance=0.0,
    iterations=3,
    warmup=1,
):
    """Measure Python/native candidate generation only after proving parity."""
    _require_native()
    reference = candidate_pairs(index, tolerance, backend="python")
    native = candidate_pairs(index, tolerance, backend="native")
    _require_parity(reference, native, "candidate-pair")

    python_result = benchmark(
        "candidate_pairs_python",
        lambda: candidate_pairs(index, tolerance, backend="python"),
        iterations=iterations,
        warmup=warmup,
    )
    native_result = benchmark(
        "candidate_pairs_native",
        lambda: candidate_pairs(index, tolerance, backend="native"),
        iterations=iterations,
        warmup=warmup,
    )
    return python_result, native_result


def benchmark_radius_query_backends(
    index,
    queries,
    iterations=3,
    warmup=1,
):
    """Measure batched radius-query backends only after proving parity."""
    _require_native()
    query_specs = tuple(queries)
    reference = radius_queries(index, query_specs, backend="python")
    native = radius_queries(index, query_specs, backend="native")
    _require_parity(reference, native, "radius-query")

    python_result = benchmark(
        "radius_queries_python",
        lambda: radius_queries(index, query_specs, backend="python"),
        iterations=iterations,
        warmup=warmup,
    )
    native_result = benchmark(
        "radius_queries_native",
        lambda: radius_queries(index, query_specs, backend="native"),
        iterations=iterations,
        warmup=warmup,
    )
    return python_result, native_result


def backend_timing_summary(python_result, native_result):
    ratio = (
        None
        if python_result.median_seconds <= 0
        else native_result.median_seconds / python_result.median_seconds
    )
    return {
        "python_seconds": python_result.median_seconds,
        "native_seconds": native_result.median_seconds,
        "native_to_python_ratio": ratio,
        "native_faster": None if ratio is None else ratio < 1.0,
    }
