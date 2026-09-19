from __future__ import annotations

import ctypes
import os
from math import hypot
from ctypes.util import find_library
from functools import lru_cache
from pathlib import Path


_ABI_VERSION = 2
_OK = 0
_BUFFER_TOO_SMALL = 1
_INVALID_ARGUMENT = 2
_UNSUPPORTED_RANGE = 3
_INTERNAL_ERROR = 4


class NativeBackendUnavailable(RuntimeError):
    pass


class NativeBackendLoadError(RuntimeError):
    pass


class NativeBackendUnsupported(RuntimeError):
    pass


class _NativeAABB(ctypes.Structure):
    _fields_ = [
        ("min_x", ctypes.c_double),
        ("min_y", ctypes.c_double),
        ("max_x", ctypes.c_double),
        ("max_y", ctypes.c_double),
    ]


class _NativePair(ctypes.Structure):
    _fields_ = [
        ("first", ctypes.c_uint32),
        ("second", ctypes.c_uint32),
    ]


class _NativePointQuery(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("radius", ctypes.c_double),
    ]


class _NativeQueryMatch(ctypes.Structure):
    _fields_ = [
        ("query", ctypes.c_uint32),
        ("point", ctypes.c_uint32),
    ]


@lru_cache(maxsize=1)
def _library_candidates() -> tuple[str, ...]:
    candidates: list[str] = []
    configured = os.environ.get("PHOTONX_NATIVE_LIBRARY")
    if configured:
        candidates.append(configured)

    discovered = find_library("photonx_native")
    if discovered:
        candidates.append(discovered)

    package_dir = Path(__file__).resolve().parent
    for name in (
        "photonx_native.dll",
        "libphotonx_native.so",
        "libphotonx_native.dylib",
    ):
        candidate = package_dir / name
        if candidate.exists():
            candidates.append(str(candidate))

    return tuple(dict.fromkeys(candidates))


def _configure_library(library: ctypes.CDLL) -> ctypes.CDLL:
    library.photonx_native_abi_version.argtypes = []
    library.photonx_native_abi_version.restype = ctypes.c_uint32
    if int(library.photonx_native_abi_version()) != _ABI_VERSION:
        raise NativeBackendLoadError("unsupported PHOTONX native ABI version")

    library.photonx_candidate_pairs.argtypes = [
        ctypes.POINTER(_NativeAABB),
        ctypes.c_uint32,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.POINTER(_NativePair),
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    library.photonx_candidate_pairs.restype = ctypes.c_int

    library.photonx_point_radius_candidates.argtypes = [
        ctypes.POINTER(_NativeAABB),
        ctypes.c_uint32,
        ctypes.POINTER(_NativePointQuery),
        ctypes.c_uint32,
        ctypes.c_double,
        ctypes.POINTER(_NativeQueryMatch),
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    library.photonx_point_radius_candidates.restype = ctypes.c_int
    return library


@lru_cache(maxsize=1)
def _load_library() -> ctypes.CDLL:
    candidates = _library_candidates()
    if not candidates:
        raise NativeBackendUnavailable("no native library discovered")

    errors: list[str] = []
    for candidate in candidates:
        try:
            return _configure_library(ctypes.CDLL(candidate))
        except (OSError, AttributeError, NativeBackendLoadError) as exc:
            errors.append(f"{candidate}: {exc}")

    raise NativeBackendLoadError("; ".join(errors))


def native_available() -> bool:
    try:
        _load_library()
    except NativeBackendUnavailable:
        return False
    return True


def native_candidate_pairs(index, tolerance: float = 0.0):
    library = _load_library()
    ids = tuple(index.ids())

    if len(ids) > 0xFFFFFFFF:
        raise NativeBackendUnsupported("native backend supports at most 2^32-1 boxes")

    try:
        tolerance_value = float(tolerance)
        cell_size = float(index.cell_size)
    except (TypeError, ValueError, AttributeError) as exc:
        raise NativeBackendUnsupported("index/tolerance is not native-compatible") from exc

    if tolerance_value < 0.0:
        raise NativeBackendUnsupported(
            "negative tolerance keeps the Python reference semantics"
        )

    box_array_type = _NativeAABB * len(ids)
    native_boxes = box_array_type(
        *(
            _NativeAABB(
                float(index.box(obj_id).min_x),
                float(index.box(obj_id).min_y),
                float(index.box(obj_id).max_x),
                float(index.box(obj_id).max_y),
            )
            for obj_id in ids
        )
    )

    required = ctypes.c_uint32(0)
    status = int(
        library.photonx_candidate_pairs(
            native_boxes,
            ctypes.c_uint32(len(ids)),
            ctypes.c_double(tolerance_value),
            ctypes.c_double(cell_size),
            None,
            ctypes.c_uint32(0),
            ctypes.byref(required),
        )
    )

    if status == _OK and required.value == 0:
        return []
    if status not in (_OK, _BUFFER_TOO_SMALL):
        _raise_status(status)

    out_type = _NativePair * required.value
    out = out_type()
    written = ctypes.c_uint32(0)
    status = int(
        library.photonx_candidate_pairs(
            native_boxes,
            ctypes.c_uint32(len(ids)),
            ctypes.c_double(tolerance_value),
            ctypes.c_double(cell_size),
            out,
            ctypes.c_uint32(required.value),
            ctypes.byref(written),
        )
    )
    if status != _OK:
        _raise_status(status)
    if written.value != required.value:
        raise NativeBackendUnavailable(
            "native backend changed pair count between sizing and fill calls"
        )

    return [
        (ids[out[i].first], ids[out[i].second])
        for i in range(written.value)
    ]


def native_radius_queries(index, queries):
    library = _load_library()
    ids = tuple(index.ids())
    query_specs = tuple((float(x), float(y), float(radius)) for x, y, radius in queries)

    if len(ids) > 0xFFFFFFFF or len(query_specs) > 0xFFFFFFFF:
        raise NativeBackendUnsupported(
            "native backend supports at most 2^32-1 boxes and queries"
        )

    try:
        cell_size = float(index.cell_size)
    except (TypeError, ValueError, AttributeError) as exc:
        raise NativeBackendUnsupported("index is not native-compatible") from exc

    box_array_type = _NativeAABB * len(ids)
    native_boxes = box_array_type(
        *(
            _NativeAABB(
                float(index.box(obj_id).min_x),
                float(index.box(obj_id).min_y),
                float(index.box(obj_id).max_x),
                float(index.box(obj_id).max_y),
            )
            for obj_id in ids
        )
    )

    native_query_type = _NativePointQuery * len(query_specs)
    native_queries = native_query_type(
        *(
            _NativePointQuery(x, y, max(0.0, radius))
            for x, y, radius in query_specs
        )
    )

    required = ctypes.c_uint32(0)
    status = int(
        library.photonx_point_radius_candidates(
            native_boxes,
            ctypes.c_uint32(len(ids)),
            native_queries,
            ctypes.c_uint32(len(query_specs)),
            ctypes.c_double(cell_size),
            None,
            ctypes.c_uint32(0),
            ctypes.byref(required),
        )
    )

    if status == _OK and required.value == 0:
        return [[] for _ in query_specs]
    if status not in (_OK, _BUFFER_TOO_SMALL):
        _raise_status(status)

    out_type = _NativeQueryMatch * required.value
    out = out_type()
    written = ctypes.c_uint32(0)
    status = int(
        library.photonx_point_radius_candidates(
            native_boxes,
            ctypes.c_uint32(len(ids)),
            native_queries,
            ctypes.c_uint32(len(query_specs)),
            ctypes.c_double(cell_size),
            out,
            ctypes.c_uint32(required.value),
            ctypes.byref(written),
        )
    )
    if status != _OK:
        _raise_status(status)
    if written.value != required.value:
        raise NativeBackendUnavailable(
            "native backend changed radius-candidate count between sizing and fill calls"
        )

    results = [[] for _ in query_specs]
    for i in range(written.value):
        query_index = int(out[i].query)
        point_index = int(out[i].point)
        if query_index >= len(query_specs) or point_index >= len(ids):
            raise NativeBackendUnavailable(
                "native backend returned an out-of-range radius candidate"
            )
        x, y, radius = query_specs[query_index]
        obj_id = ids[point_index]
        box = index.box(obj_id)
        center_x = (float(box.min_x) + float(box.max_x)) / 2.0
        center_y = (float(box.min_y) + float(box.max_y)) / 2.0
        distance = hypot(x - center_x, y - center_y)
        if distance <= radius:
            results[query_index].append((distance, obj_id))

    for result in results:
        result.sort(key=lambda item: (item[0], item[1]))
    return results


def _raise_status(status: int) -> None:
    if status in (_INVALID_ARGUMENT, _UNSUPPORTED_RANGE):
        raise NativeBackendUnsupported(f"native backend rejected input (status={status})")
    if status == _INTERNAL_ERROR:
        raise NativeBackendUnavailable("native backend reported an internal error")
    raise NativeBackendUnavailable(f"unexpected native backend status={status}")
