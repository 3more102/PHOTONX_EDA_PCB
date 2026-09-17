# Contributing

1. Do not silently ignore unsupported manufacturing commands.
2. Add a regression fixture before fixing a parser bug.
3. Preserve source provenance for newly reconstructed object types.
4. Keep inference outputs explicitly labeled as hypotheses until supported by evidence.
5. Never convert `unknown` into a definite value merely to satisfy an exporter.
6. Run `pytest -q` before proposing changes.
