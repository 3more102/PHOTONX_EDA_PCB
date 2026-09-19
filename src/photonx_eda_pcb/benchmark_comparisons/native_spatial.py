from __future__ import annotations

from photonx_eda_pcb.performance_profiles import benchmark
from photonx_eda_pcb.spatial_connectivity import candidate_pairs
from photonx_eda_pcb.spatial_connectivity.native_backend import (
    NativeBackendUnavailable,
    native_available,
)


def benchmark_candidate_pair_backends(
    index,
    tolerance: float = 0.0,
    *,
    iterations: int = 3,
    warmup: int = 1,
):
    """Benchmark Python and native broad phases after proving result parity."""
    expected = candidate_pairs(index, tolerance, backend="python")
    if not native_available():
        raise NativeBackendUnavailable(
            "native backend is required for candidate-pair backend benchmarking"
        )

    native_expected = candidate_pairs(index, tolerance, backend="native")
    if native_expected != expected:
        raise AssertionError(
            "native candidate-pair backend does not match the Python reference"
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


def _stable_result_size(result):
    sizes = {sample.result_size for sample in result.samples}
    if len(sizes) != 1:
        raise ValueError(f"{result.name} produced inconsistent benchmark result sizes")
    return next(iter(sizes))


def native_candidate_pair_summary(python_result, native_result):
    """Return timing and parity metadata without enforcing a speedup threshold."""
    python_size = _stable_result_size(python_result)
    native_size = _stable_result_size(native_result)
    if python_size != native_size:
        raise ValueError("Python/native benchmark result sizes do not match")

    ratio = (
        None
        if python_result.median_seconds <= 0
        else native_result.median_seconds / python_result.median_seconds
    )
    speedup = (
        None
        if native_result.median_seconds <= 0
        else python_result.median_seconds / native_result.median_seconds
    )
    return {
        "pairs": python_size,
        "python_seconds": python_result.median_seconds,
        "native_seconds": native_result.median_seconds,
        "native_to_python_ratio": ratio,
        "python_over_native_speedup": speedup,
    }
