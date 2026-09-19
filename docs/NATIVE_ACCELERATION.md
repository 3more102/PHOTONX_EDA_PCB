# Native C/C++ acceleration

PHOTONX remains Python-first at the orchestration, parser, provenance, and exact-geometry layers. Native code is introduced only behind parity-checked boundaries where it can accelerate deterministic candidate generation without changing engineering meaning.

## Stage 1: spatial broad phase

The first native component is a C++17 spatial-hash implementation exposed through a small C ABI.

It accelerates `spatial_connectivity.candidate_pairs()` only. Candidate generation is a broad-phase optimization: exact Shapely/Euclidean predicates in connectivity and DRC remain authoritative.

The Python API keeps the existing call form and adds an optional backend selector:

- `backend="auto"`: use the native library when available and compatible, otherwise use Python.
- `backend="python"`: force the reference implementation.
- `backend="native"`: require the native implementation and report unavailability/unsupported input explicitly.

The native library is optional. A missing compiler or missing shared library must not make the normal Python package unusable.
If no native library is discovered, `auto` falls back to Python. If a native library is discovered/configured but fails to load, exposes the wrong ABI, or is missing required symbols, that installation error is surfaced instead of being silently hidden by fallback.

## Build

Linux/macOS:

    cmake -S native -B build/native -DCMAKE_BUILD_TYPE=Release
    cmake --build build/native --config Release

Windows with a CMake-supported Visual Studio toolchain:

    cmake -S native -B build/native -DCMAKE_BUILD_TYPE=Release
    cmake --build build/native --config Release

Point Python at the resulting shared library with `PHOTONX_NATIVE_LIBRARY`.

The CI workflow builds the native library and executes the full pytest suite with it enabled so native/Python parity regressions are exercised continuously.

## Safety contract

The native backend:

1. returns deterministic pairs ordered by the existing string-ID order;
2. preserves inclusive AABB intersection semantics;
3. accepts only finite, normalized boxes, finite non-negative tolerance, and positive finite cell size;
4. returns an unsupported-range status instead of attempting pathological cell expansions;
5. never asserts copper connectivity itself.

Unsupported native inputs fall back to the Python reference path in `auto` mode.

## Stage 2: batch point-radius candidates

ABI v2 adds `photonx_point_radius_candidates()`, a C++17 batch broad-phase for point-radius queries. Python sends many query centers/radii in one call, receives deterministic candidate IDs, and then applies the existing Euclidean distance predicate in Python. This preserves the core safety rule: native code may accelerate candidate generation, but it does not decide exact engineering relationships.

The Python `batch_radius_query()` and `radius_query()` APIs expose `python`, `native`, and `auto` backends. The existing Python path remains the default until benchmark evidence justifies changing production defaults.

Stage 2 preserves:

1. exact Euclidean `distance <= radius` semantics after native broad-phase selection;
2. deterministic result ordering by distance and then string ID;
3. batched native grid construction so repeated queries do not rebuild the C++ spatial hash one query at a time;
4. fail-closed handling for invalid/non-finite native inputs;
5. Python fallback when the native backend is unavailable or cannot represent the request in `auto` mode.

This kernel is suitable for drill association, via-span lookup, footprint clustering, and component-pair candidate generation once those call sites opt into the batch path.

## Next native stages

The next safe candidates are:

1. benchmark and wire batch radius queries into reconstruction hot paths where they outperform the Python index;
2. persistent native spatial-index handles when repeated cross-stage reuse justifies lifecycle complexity;
3. benchmark-gated default selection for native connectivity candidate generation;
4. only after parity evidence, selected computational-geometry kernels with explicit tolerance contracts.

Gerber/Excellon parsing, provenance, fail-closed diagnostics, and semantic inference should not be migrated merely for language uniformity. They should move only when a measured bottleneck and a parity strategy exist.
