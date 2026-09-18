# Changelog

## Unreleased

- Added production-path Gerber step-and-repeat support for the currently supported linear geometry subset.
- Expanded flashes, linear draws, and outline segments deterministically while preserving source provenance.
- Added unit-aware repeat spacing, deterministic per-instance IDs, and explicit `gerber_step_repeat` evidence.
- Added focused regression coverage for flash expansion, track expansion/termination, and inch-to-mm spacing.
- Added production-path G75 multi-quadrant G02/G03 Gerber arc support using I/J center offsets with circular draw apertures.
- Added coordinate-resolution-aware radius validation and deterministic arc tessellation with a 0.005 mm chord-error target.
- Added explicit `gerber_arc_tessellation` provenance evidence and step-repeat composition for generated arc segments.
- Added generic directory/single-file/ZIP manufacturing ingestion with recursive discovery, content sniffing, X2/filename layer inference, and parser-backed preflight.
- Added legacy Gerber/Excellon compatibility hardening including modal D operations, UTF-8 BOM handling, G70/G71, M71/M72, and bounded content sniffing.
- Added safe production support for single positive centered-circle Gerber aperture macros, including parameterized diameters and correct active-unit conversion.
- Complex aperture macros, G74 single-quadrant arcs, Gerber regions, aperture blocks, and Excellon routed arcs remain explicit fail-closed boundaries.

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
