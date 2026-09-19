# Rust acceleration

PHOTONX keeps Python as the orchestration and public-API layer while allowing
performance-critical deterministic kernels to move to Rust behind narrow,
reviewable interfaces.

## Current native boundary

The first Rust kernel accelerates spatial broad-phase candidate generation for
same-layer copper connectivity.

The safety boundary is deliberate:

1. Python/Shapely still constructs the authoritative copper geometry.
2. Rust receives only object IDs and axis-aligned bounding boxes.
3. Rust returns deterministic candidate ID pairs.
4. Python/Shapely still performs the exact buffered intersection predicate
   before a connectivity edge is created.

The native backend therefore cannot create a physical-net connection merely
because two bounding boxes are candidates.

If the extension is not installed, PHOTONX automatically uses the existing
Python SpatialHashIndex implementation. An installed native backend is not
silently ignored if it raises an execution error.

## Build the extension locally

From the repository root, inside the same virtual environment used for PHOTONX:

~~~bash
python -m pip install "maturin>=1.14,<2"
maturin develop --manifest-path native/Cargo.toml --features python --release
~~~

Verify the extension:

~~~bash
python -c "from photonx_eda_pcb.native_backend import rust_spatial_available; print(rust_spatial_available())"
~~~

Run the relevant regressions:

~~~bash
pytest -q tests/test_native_spatial_backend.py tests/test_connectivity_spatial_parity_phase28.py
cargo test --manifest-path native/Cargo.toml
~~~

## Design rules for future Rust kernels

- Preserve deterministic ordering and stable IDs.
- Keep evidence/provenance and semantic decisions in the existing model layer.
- Use Rust first for measurable bottlenecks: spatial indexing, geometry
  candidate generation, routing/search kernels, and other CPU-heavy pure
  computations.
- Keep a Python fallback until the native path has parity tests and supported
  wheels for target platforms.
- Fail closed on malformed or non-finite numeric inputs.
- Do not replace exact geometry predicates with bounding-box approximations.
