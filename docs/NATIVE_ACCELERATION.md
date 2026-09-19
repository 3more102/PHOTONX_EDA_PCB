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

### Optional self-contained wheel

A normal package build remains Python-only and does not require CMake or a C++ compiler. To produce a platform-specific wheel that embeds the native library beside the Python adapter, opt in at build time:

Linux/macOS:

    PHOTONX_BUILD_NATIVE=1 python -m build --wheel

Windows PowerShell:

    $env:PHOTONX_BUILD_NATIVE="1"
    python -m build --wheel

The build hook compiles the C++17 library with CMake, checks that its exported ABI version matches the Python adapter, and copies the shared library into `photonx_eda_pcb/spatial_connectivity`. The existing loader discovers that package-local library automatically, so an installed native wheel does not require `PHOTONX_NATIVE_LIBRARY`.

Source distributions include the `native/` CMake project, so downstream builders can opt into the same native-wheel path from an sdist.

The Linux CI workflow builds the native library and executes the full pytest suite with it enabled so native/Python parity regressions are exercised continuously. Dedicated portability jobs build and load the native library on Linux, macOS, and Windows, then build/install a self-contained native wheel and verify package-local discovery.

## Stage 2: batch point-radius broad phase

The native ABI also supports batched point-radius candidate generation. PHOTONX builds the center-point spatial hash once for a batch of queries and returns only square-window candidates. Python then recomputes the authoritative Euclidean distance with `math.hypot`, applies the exact `distance <= radius` predicate, and sorts by `(distance, id)`.

The batch path is used by drill association, footprint clustering and metrics, and component-pair inference and metrics. This reduces repeated Python-to-native transitions while preserving the previous Python result contract.

The main spatial consumers expose the same backend contract as the low-level API:

- `attach_drills(..., backend="auto" | "python" | "native")`
- `infer_component_hypotheses(..., backend="auto" | "python" | "native")`
- `cluster_pads(..., backend="auto" | "python" | "native")`

This makes parity testing and deployment policy explicit at the workflow boundary instead of requiring callers to depend on environment discovery alone.

## Stage 3: persistent native spatial indexes

Repeated connectivity and radius-query calls now reuse opaque C++ spatial-index handles instead of rebuilding native grids on every ctypes transition. Both AABB broad-phase and point-center broad-phase indexes are cached per `SpatialHashIndex` revision.

`SpatialHashIndex` exposes a monotonic mutation revision. An insert invalidates the cached native view automatically on the next call. Duck-typed indexes without a trustworthy weak-key + revision contract use ephemeral native handles, so mutable custom indexes cannot accidentally reuse stale native geometry.

Cache invalidation only removes the cache reference. An active query keeps a strong borrowed reference until it returns, preventing use-after-free when another thread clears or replaces the cache. Python still owns exact Euclidean filtering, deterministic ID mapping, and all PCB connectivity meaning.

## Safety contract

The native backend:

1. returns deterministic pairs ordered by the existing string-ID order;
2. preserves inclusive AABB intersection semantics;
3. accepts only finite, normalized boxes, finite non-negative tolerance, and positive finite cell size;
4. returns an unsupported-range status instead of attempting pathological cell expansions;
5. preflights a global query-cell work budget before scanning and caps native output growth, preventing oversized batches from driving unbounded CPU or memory use inside the C++ layer;
6. never asserts copper connectivity itself.

Unsupported native inputs fall back to the Python reference path in `auto` mode.

## Next native stages

The next safe candidates are:

1. benchmark-gated crossover thresholds so small workloads stay on the Python reference path when that is faster;
2. benchmark coverage for repeated-query workloads to quantify persistent-index wins;
3. automated release-wheel production/signing for supported platform/Python combinations;
4. only after parity evidence, selected computational-geometry kernels with explicit tolerance contracts.

Gerber/Excellon parsing, provenance, fail-closed diagnostics, and semantic inference should not be migrated merely for language uniformity. They should move only when a measured bottleneck and a parity strategy exist.
