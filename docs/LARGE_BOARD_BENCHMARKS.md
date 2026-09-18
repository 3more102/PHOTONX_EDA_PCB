# Large-board Benchmarks

large_board_benchmarks defines deterministic synthetic grid scenarios around roughly 1k, 3k and 7k copper objects.

The benchmark runner compares brute-force and spatial physical-connectivity paths and records candidate-pair reduction plus measured timing.

These scenarios are intentionally not used as strict CI timing gates because shared CI timing is noisy. Correctness parity remains mandatory in CI.
