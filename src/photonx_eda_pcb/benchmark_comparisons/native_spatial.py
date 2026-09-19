from __future__ import annotations

import math
import platform

from photonx_eda_pcb.performance_profiles import benchmark
from photonx_eda_pcb.spatial_connectivity import AABB, SpatialHashIndex, candidate_pairs
from photonx_eda_pcb.spatial_connectivity.native_backend import (
    NativeBackendUnavailable,
    native_available,
)
from photonx_eda_pcb.spatial_connectivity.points import radius_queries


def build_native_benchmark_index(object_count: int, *, cell_size: float = 1.0) -> SpatialHashIndex:
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
    tolerance: float = 0.30,
    *,
    iterations: int = 3,
    warmup: int = 1,
):
    expected = candidate_pairs(index, tolerance, backend="python")
    actual = candidate_pairs(index, tolerance, backend="native")
    if actual != expected:
        raise AssertionError("native candidate-pair output differs from Python reference")

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
    *,
    iterations: int = 3,
    warmup: int = 1,
):
    specs = tuple((float(x), float(y), float(radius)) for x, y, radius in queries)
    expected = radius_queries(index, specs, backend="python")
    actual = radius_queries(index, specs, backend="native")
    if actual != expected:
        raise AssertionError("native radius-query output differs from Python reference")

    python_result = benchmark(
        "radius_queries_python",
        lambda: radius_queries(index, specs, backend="python"),
        iterations=iterations,
        warmup=warmup,
    )
    native_result = benchmark(
        "radius_queries_native",
        lambda: radius_queries(index, specs, backend="native"),
        iterations=iterations,
        warmup=warmup,
    )
    return python_result, native_result


def native_backend_comparison_summary(python_result, native_result) -> dict:
    python_seconds = float(python_result.median_seconds)
    native_seconds = float(native_result.median_seconds)
    ratio = None if python_seconds <= 0.0 else native_seconds / python_seconds
    speedup = None if native_seconds <= 0.0 else python_seconds / native_seconds
    return {
        "python_seconds": python_seconds,
        "native_seconds": native_seconds,
        "native_to_python_ratio": ratio,
        "python_over_native_speedup": speedup,
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

    if not native_available():
        raise NativeBackendUnavailable("native spatial backend is not available")

    index = build_native_benchmark_index(count, cell_size=cell_size)
    ids = index.ids()
    queries = tuple(
        (
            (index.box(obj_id).min_x + index.box(obj_id).max_x) / 2.0,
            (index.box(obj_id).min_y + index.box(obj_id).max_y) / 2.0,
            radius,
        )
        for obj_id in ids
    )

    candidate_python, candidate_native = benchmark_candidate_pair_backends(
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

    candidate_output = candidate_pairs(index, tolerance, backend="python")
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
            **native_backend_comparison_summary(candidate_python, candidate_native),
            "result_pairs": len(candidate_output),
        },
        "radius_queries": {
            **native_backend_comparison_summary(radius_python, radius_native),
            "result_matches": sum(len(items) for items in radius_output),
        },
    }
