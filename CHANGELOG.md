# Changelog

## 0.2.0

- Rebuilt the project around evidence/provenance rather than demo-only objects.
- Added deterministic object IDs.
- Added strict Gerber and Excellon parsers that reject unsupported constructs instead of silently dropping them.
- Added manufacturing-file discovery and layer inference.
- Added physical connectivity graph and deterministic physical-net groups.
- Added conservative component hypotheses with explicit confidence/evidence.
- Added independent model validation with fault-injection tests.
- Added JSON reconstruction bundles and experimental KiCad export.
- Added model-backed GUI viewer/inspector.
- Expanded regression suite to 17 tests.
