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

## Stage 2: batch point-radius broad phase

The native ABI also supports batched point-radius candidate generation. PHOTONX builds the center-point spatial hash once for a batch of queries and returns only square-window candidates. Python then recomputes the authoritative Euclidean distance with `math.hypot`, applies the exact `distance <= radius` predicate, and sorts by `(distance, id)`.

The batch path is used by drill association, footprint clustering and metrics, and component-pair inference and metrics. This reduces repeated Python-to-native transitions while preserving the previous Python result contract.

## Stage 3: benchmark evidence

PHOTONX includes a deterministic native-vs-Python spatial benchmark path. It checks output parity before collecting timings, so a backend mismatch fails instead of producing a misleading performance comparison.

After building the shared library and setting `PHOTONX_NATIVE_LIBRARY`, run:

    photonx native-benchmark --objects 1000 --iterations 3

Optional controls include `--warmup`, `--tolerance`, `--radius`, `--cell-size`, and `--output`. The command reports JSON containing the workload parameters, Python/platform metadata, candidate-pair result size, radius-query match count, median timings, native/Python timing ratios, and observed speedup. If the native backend is unavailable or incompatible, the command exits non-zero and reports the failure instead of silently benchmarking the Python fallback.

These measurements are evidence, not a product performance claim. PHOTONX does not use a hard-coded crossover threshold from a single CI machine or one benchmark run.

## Safety contract

The native backend:

1. returns deterministic pairs ordered by the existing string-ID order;
2. preserves inclusive AABB intersection semantics;
3. accepts only finite, normalized boxes, finite non-negative tolerance, and positive finite cell size;
4. returns an unsupported-range status instead of attempting pathological cell expansions;
5. never asserts copper connectivity itself.

Unsupported native inputs fall back to the Python reference path in `auto` mode.

## Next native stages

The next safe candidates are:

1. collect benchmark evidence across representative board sizes/platforms before considering automatic backend crossover thresholds;
2. cross-platform packaging of the optional native library;
3. persistent native index handles only if profiling shows repeated index rebuild cost is material in real call paths;
4. only after parity evidence, selected computational-geometry kernels with explicit tolerance contracts.

Gerber/Excellon parsing, provenance, fail-closed diagnostics, and semantic inference should not be migrated merely for language uniformity. They should move only when a measured bottleneck and a parity strategy exist.
