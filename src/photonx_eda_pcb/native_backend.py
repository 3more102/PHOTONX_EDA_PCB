from __future__ import annotations

from collections.abc import Iterable

try:
    import _photonx_native as _native
except ImportError:
    _native = None


AabbRecord = tuple[str, float, float, float, float]
SpatialPair = tuple[str, str]


def rust_spatial_available() -> bool:
    """Return whether the optional PHOTONX Rust extension is importable."""
    return _native is not None


def try_native_candidate_pairs(
    boxes: Iterable[AabbRecord],
    tolerance: float,
    cell_size: float,
) -> list[SpatialPair] | None:
    """Run Rust broad-phase pairing when available, otherwise request fallback.

    Returning None means the extension is not installed. Native execution
    errors are intentionally not swallowed: an installed accelerator must fail
    visibly rather than silently changing behavior.
    """
    if _native is None:
        return None

    records = [
        (
            str(obj_id),
            float(min_x),
            float(min_y),
            float(max_x),
            float(max_y),
        )
        for obj_id, min_x, min_y, max_x, max_y in boxes
    ]
    return [
        (str(left), str(right))
        for left, right in _native.candidate_pairs_aabb(
            records,
            float(tolerance),
            float(cell_size),
        )
    ]
