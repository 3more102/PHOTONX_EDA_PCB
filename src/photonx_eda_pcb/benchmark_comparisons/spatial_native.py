from __future__ import annotations

import math
import platform

from photonx_eda_pcb.performance_profiles import benchmark
from photonx_eda_pcb.spatial_connectivity import (
    AABB,
    SpatialHashIndex,
    candidate_pairs,
)
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


def build_native_benchmark_index(
    object_count: int,
    *,
    cell_size: float = 1.0,
) -> SpatialHashIndex:
    """Build a deterministic mixed-overlap workload for backend comparisons."""
    count = int(object_count)
    cell = float(cell_size)
    if count <= 0:
        raise ValueError("object_count must be positive")
    if not math.isfinite(cell) or cell <= 0.0:
        raise ValueError("cell_size must be positive and finite")

    side = max(1, math.ceil(math.sqrt(count)))
    index = SpatialHashIndex(cell)
    for i in range(count):
        row, col = divmod(i, side)
        x = col * 0.75
        y = row * 0.75
        index.insert(
            f"obj-{i:08d}",
            AABB(x, y, x + 0.50, y + 0.50),
        )
    return index


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


def native_spatial_benchmark_report(
    object_count: int = 1000,
    *,
    iterations: int = 3,
    warmup: int = 1,
    tolerance: float = 0.30,
    radius: float = 1.0,
    cell_size: float = 1.0,
) -> dict:
    """Run parity-gated spatial benchmarks and return machine-readable evidence."""
    count = int(object_count)
    iterations = int(iterations)
    warmup = int(warmup)
    tolerance = float(tolerance)
    radius = float(radius)
    cell_size = float(cell_size)

    if count <= 0:
        raise ValueError("object_count must be positive")
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if not math.isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("tolerance must be finite and non-negative")
    if not math.isfinite(radius) or radius < 0.0:
        raise ValueError("radius must be finite and non-negative")
    if not math.isfinite(cell_size) or cell_size <= 0.0:
        raise ValueError("cell_size must be positive and finite")

    _require_native()
    index = build_native_benchmark_index(count, cell_size=cell_size)
    queries = tuple(
        (
            (box.min_x + box.max_x) / 2.0,
            (box.min_y + box.max_y) / 2.0,
            radius,
        )
        for obj_id in index.ids()
        for box in (index.box(obj_id),)
    )

    pair_python, pair_native = benchmark_candidate_pair_backends(
        index,
        tolerance,
        iterations=iterations,
        warmup=warmup,
    )
    radius_python, radius_native = benchmark_radius_query_backends(
        index,
        queries,
        iterations=iterations,
        warmup=warmup,
    )

    pair_output = candidate_pairs(index, tolerance, backend="python")
    radius_output = radius_queries(index, queries, backend="python")

    return {
        "native_available": True,
        "objects": count,
        "queries": len(queries),
        "parameters": {
            "iterations": iterations,
            "warmup": warmup,
            "tolerance": tolerance,
            "radius": radius,
            "cell_size": cell_size,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "candidate_pairs": {
            **backend_timing_summary(pair_python, pair_native),
            "result_pairs": len(pair_output),
        },
        "radius_queries": {
            **backend_timing_summary(radius_python, radius_native),
            "result_matches": sum(len(items) for items in radius_output),
        },
    }
