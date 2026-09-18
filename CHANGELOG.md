# Changelog

## Unreleased

- Hardened permissive Gerber parsing so rectangular/obround D01 draws are skipped with diagnostics instead of being approximated as width-only tracks; current-point state is still advanced correctly.
- Validated standard Gerber rectangle/obround outer dimensions at parse time; zero X/Y sizes now fail closed instead of entering reconstruction as invalid geometry.
- Hardened Gerber layer-polarity handling: `%LPD*%` remains supported, while `%LPC*%` fails closed in strict mode and suppresses file geometry in permissive mode so clear subtraction cannot be emitted as positive material.
- Verified merged commit `273e153` on Python 3.11, 3.12, and 3.13 with 688 passing tests and 2 existing collection warnings.
- Corrected standard Gerber aperture parsing so circle hole modifiers are never misread as Y dimensions; C/R/O apertures with hole modifiers now fail closed until aperture-hole subtraction is modeled.
- Hardened X2 `.FilePolarity` handling: explicit positive polarity is accepted, negative polarity fails closed in strict mode, and permissive parsing suppresses geometry instead of emitting inverted material semantics.
- Added production-path Gerber step-and-repeat support for the currently supported linear geometry subset.
- Expanded flashes, linear draws, and outline segments deterministically while preserving source provenance.
- Added unit-aware repeat spacing, deterministic per-instance IDs, and explicit `gerber_step_repeat` evidence.
- Added focused regression coverage for flash expansion, track expansion/termination, and inch-to-mm spacing.
- Verified merged commit `556beaf` on Python 3.11, 3.12, and 3.13 with 673 passing tests and 2 existing collection warnings.
- Added production-path G75 multi-quadrant G02/G03 Gerber arc support using I/J center offsets with circular draw apertures.
- Added coordinate-resolution-aware radius validation and deterministic arc tessellation with a 0.005 mm chord-error target.
- Added explicit `gerber_arc_tessellation` provenance evidence and step-repeat composition for generated arc segments.
- Added safe production support for single positive centered-circle Gerber aperture macros, including parameterized diameters and active-unit conversion.
- Added bounded legacy G74 single-quadrant G02/G03 arc support using unsigned I/J distances, four-candidate center resolution, <=90-degree sweep enforcement, and fail-closed ambiguity handling.
- Kept Gerber regions, complex aperture macros, and aperture blocks explicitly unsupported.
- Added standard XNC G02/G03 X/Y/A-radius routed-arc support with <=180-degree center resolution, deterministic tessellation, and fail-closed invalid geometry.

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
