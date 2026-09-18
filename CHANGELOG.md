# Changelog

## Unreleased

- Added production-path Gerber step-and-repeat support for the currently supported linear geometry subset.
- Expanded flashes, linear draws, and outline segments deterministically while preserving source provenance.
- Added unit-aware repeat spacing, deterministic per-instance IDs, and explicit `gerber_step_repeat` evidence.
- Added focused regression coverage for flash expansion, track expansion/termination, and inch-to-mm spacing.
- Verified the merged code on Python 3.11, 3.12, and 3.13 with 618 passing tests and 2 existing collection warnings.

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
