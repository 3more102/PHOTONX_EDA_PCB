# Benchmarking harness

Benchmarks record warm-up, repeated durations, environment metadata and peak traced memory. Performance results are meaningful only when fixture size, hardware, Python version and configuration are identified. No benchmark number is treated as a product claim by default.

Native spatial acceleration uses an additional parity gate: the Python and C++ results must match exactly before timing evidence is returned. Use `benchmark_candidate_pair_backends()` for AABB candidate-pair generation, `benchmark_radius_query_backends()` for batched point-radius queries, and `backend_timing_summary()` to report the measured native/Python median-time ratio.

For reproducible command-line evidence, either install a self-contained native wheel or build/configure the native library manually, then run:

    photonx native-benchmark --objects 1000 --iterations 3

Use `--output build/native-benchmark.json` to retain the JSON report. The report records workload parameters, Python/platform metadata, result counts, median timings, and the observed native/Python ratio. If native loading, range support, or parity fails, the command exits non-zero instead of presenting fallback timing as native timing.

Do not hard-code an `auto` backend crossover threshold from one machine or one synthetic fixture. Any future threshold must be justified by repeatable measurements across representative board sizes, spatial densities, cell sizes, tolerances, radius distributions, and batch sizes.
