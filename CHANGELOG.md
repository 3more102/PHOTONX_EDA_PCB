# Changelog

## Unreleased

- Hardened Gerber unit semantics: dimensional data now requires explicit `MO` or supported legacy `G70/G71`, and conflicting unit switches fail closed with permissive file-geometry suppression instead of defaulting to millimeters or mixing unit systems.
- Verified merged commit `a2fd34c` on Python 3.11, 3.12, and 3.13 with 797 passing tests and 2 existing collection warnings.
- Hardened Gerber step-and-repeat state handling so malformed, non-positive, or over-limit `%SR...%` commands suppress permissive file geometry instead of falling back to a single un-repeated copy.
- Hardened Excellon linear-route and G85 failure handling so malformed commands, invalid routing state transitions, empty route termination, and unterminated routes suppress permissive file geometry instead of allowing partial routes or mixed drill/slot output.
- Verified merged commit `de1a6a2` on Python 3.11, 3.12, and 3.13 with 778 passing tests and 2 existing collection warnings.
- Hardened Excellon routed-arc failure handling so unsupported syntax, missing centers, invalid arc geometry, or invalid route state suppresses permissive file geometry instead of allowing an incomplete route to be emitted; invalid arc geometry is now a strict preflight blocker.
- Rejected zero-diameter Excellon tools and suppressed permissive file geometry so zero-width drills, slots, or routes cannot enter reconstruction.
- Hardened Excellon unit handling so tool definitions before explicit `METRIC/INCH/M71/M72` units no longer inherit the parser's default millimeter state; permissive parsing suppresses file geometry instead.
- Hardened legacy Excellon incremental coordinate modes (`G91` and `ICI,ON`): strict parsing rejects them, permissive parsing clears/suppresses file geometry, and explicit absolute `G90` / `ICI,OFF` remains supported.
- Hardened unsupported Gerber region (`G36/G37`) and aperture-block (`AB`) handling so permissive parsing suppresses file geometry instead of leaking region/block bodies as ordinary tracks or flashes.
- Recognized deprecated incremental FS notation (`%FSLI...*%` / `%FSTI...*%`) explicitly and routed it through the same fail-closed geometry suppression and preflight blocker used for `G91`.
- Verified merged commit `c457cf8` on Python 3.11, 3.12, and 3.13 with 739 passing tests and 2 existing collection warnings.
- Hardened Gerber `G91` handling so permissive parsing suppresses file geometry and preflight reports a strict blocker instead of interpreting incremental coordinates as absolute.
- Verified merged commit `5427c7a` on Python 3.11, 3.12, and 3.13 with 733 passing tests and 2 existing collection warnings.
- Hardened legacy Gerber `AS/IP/MI/OF` transform handling so permissive parsing suppresses affected file geometry instead of continuing with untransformed coordinates or image semantics.
- Verified merged commit `7721876` on Python 3.11, 3.12, and 3.13 with 722 passing tests and 2 existing collection warnings.
- Completed positive outer-size validation for standard Gerber apertures by rejecting zero-diameter circle apertures in strict, permissive, and preflight paths.
- Hardened Gerber `LM/LR/LS` aperture-transform handling: identity states remain supported, while non-identity or malformed transforms fail closed so mirrored, rotated, or scaled objects cannot be emitted with untransformed geometry.
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
