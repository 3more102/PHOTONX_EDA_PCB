# Benchmarking harness

Benchmarks record warm-up, repeated durations, environment metadata and peak traced memory. Performance results are meaningful only when fixture size, hardware, Python version and configuration are identified. No benchmark number is treated as a product claim by default.

Native spatial acceleration uses an additional parity gate: the Python and C++ results must match exactly before timing evidence is returned. Use `benchmark_candidate_pair_backends()` for AABB candidate-pair generation, `benchmark_radius_query_backends()` for batched point-radius queries, and `backend_timing_summary()` to report the measured native/Python median-time ratio.

Do not hard-code an `auto` backend crossover threshold from one machine or one synthetic fixture. Any future threshold must be justified by repeatable measurements across representative board sizes, spatial densities, cell sizes, tolerances, radius distributions, and batch sizes.
