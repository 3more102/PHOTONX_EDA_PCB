from photonx_eda_pcb.performance_profiles import benchmark
from photonx_eda_pcb.spatial_connectivity import candidate_pairs
from photonx_eda_pcb.spatial_connectivity.native_backend import (
    NativeBackendUnavailable,
    native_available,
)


def benchmark_candidate_pair_backends(
    index,
    tolerance=0.0,
    iterations=3,
    warmup=1,
):
    """Measure Python/native candidate generation only after proving parity."""
    if not native_available():
        raise NativeBackendUnavailable("native spatial backend is not available")

    reference = candidate_pairs(index, tolerance, backend="python")
    native = candidate_pairs(index, tolerance, backend="native")
    if native != reference:
        raise AssertionError(
            "native candidate-pair backend diverged from the Python reference"
        )

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


def candidate_backend_summary(python_result, native_result):
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
