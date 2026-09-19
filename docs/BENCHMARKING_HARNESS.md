# Benchmarking harness

Benchmarks record warm-up and repeated durations. Performance results are meaningful only when fixture size, hardware, Python version, platform, and configuration are identified. No benchmark number is treated as a product claim by default.

## Existing benchmark layers

PHOTONX keeps benchmark measurement separate from correctness and policy:

- `performance_profiles.benchmark()` records repeated timing samples and result sizes.
- `benchmark_comparisons` compares alternative implementations such as brute-force versus spatial connectivity.
- `benchmark_governance` can evaluate explicit regression policies when a workflow supplies appropriate evidence.
- `large_board_benchmarks` provides deterministic synthetic scaling scenarios.

Synthetic benchmark results are useful for regression detection and crossover exploration, but they do not substitute for measurements on representative real board workloads.

## Native spatial benchmark

The optional C++ spatial backend has a dedicated comparison path for both candidate-pair generation and batched point-radius queries.

Build the native library first:

    cmake -S native -B build/native -DCMAKE_BUILD_TYPE=Release
    cmake --build build/native --config Release

Then point PHOTONX at the library and run a benchmark. On Linux:

    PHOTONX_NATIVE_LIBRARY="$PWD/build/native/lib/libphotonx_native.so" \
      photonx native-benchmark --objects 1000 --iterations 3

To retain machine-readable evidence:

    photonx native-benchmark \
      --objects 3000 \
      --iterations 5 \
      --warmup 1 \
      --output build/native-benchmark.json

The benchmark checks native output against the Python reference before timing. It reports observed medians and ratios but does not enforce a timing threshold. Backend-selection policy should be based on repeated evidence across representative workloads and platforms, not a single CI measurement.

If the native library cannot be discovered, loaded, or used for the requested range, the command exits non-zero and records the error instead of timing the Python fallback as if it were native.
