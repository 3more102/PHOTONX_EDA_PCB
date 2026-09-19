# Changelog

## Unreleased

- Aligned edge-clearance metrics with the DRC copper-object model: `CopperRegion` geometry now contributes to object counts, minimum edge clearance, and outside-board metrics, with a focused regression preventing silent region omission.

- Fixed KiCad recovered-pad surface-layer pairing: back-side SMD pads now use `B.Paste`/`B.Mask` and back silkscreen references, front-side pads keep the matching front layers, and non-surface copper pads no longer invent front/back paste or mask layers.

- Hardened Gerber X2 attribute ingestion: TF/TA/TO/TD command grammar and standard-name domains are validated before metadata is preserved, while attribute fields safely decode 4- and 8-digit Unicode escapes after comma splitting. Malformed escapes, invalid Unicode scalars, raw reserved characters, invalid names/domain use, value-bearing TD commands, and malformed TO.C fail closed.


- Added an optional C++17 native spatial-acceleration backend behind a versioned C ABI. The backend provides deterministic AABB candidate-pair generation plus batched point-radius broad-phase queries used by drill association, footprint clustering/metrics, and component inference/metrics; Python remains the correctness reference and automatic fallback, exact Euclidean/connectivity predicates stay authoritative, native discovery is cached, ABI/range failures are explicit, and CI builds/loads the shared library on Python 3.11/3.12/3.13 before running the full regression suite.

- Added specification-compliant Gerber aperture-macro variable semantics and numeric hardening: AD parameters seed macro variables, ordered `$n=expression` assignments are evaluated in source order, undefined variables evaluate to zero, exact token substitution prevents `$1` from aliasing `$10`, and any redefinition is rejected. Code-1 circle reduction now requires exactly four or five finite modifiers and rejects active-unit conversion overflow, with parser/preflight regressions for supported and fail-closed paths.

- Extended Code-4 aperture-macro support beyond centered rectangle/regular-polygon reduction: any valid single-positive simple linear outline with 3–5000 vertices can now be retained exactly for D03 flashes on material layers, including irregular, concave, and off-center shapes. The production path rejects zero-length, self-touching, self-intersecting, open, non-finite, and zero-area contours; preserves primitive rotation before LM/LR/LS plus supported whole-image IR; and carries exact CopperRegion geometry through step-repeat, provenance, and ordered LPD/LPC composition. General Code-4 D01 sweeps and Edge.Cuts flashes remain fail-closed.

- Added exact production reduction for single positive Gerber aperture-macro Outline primitives (Code 4) when the explicitly closed contour is exactly a centered rectangle or centered regular polygon. Rectangle edge orientation and primitive rotation reduce to exact `R` geometry; 3–12 vertex regular outlines reduce to exact `P` geometry. Open, irregular, off-exposure, malformed, and non-reducible outlines remain fail-closed with preflight coverage.

- Extended exact single-primitive rectangular Gerber aperture-macro reduction to arbitrary finite rotation. Centered Code-20/Code-2 vector lines may now use non-axis-aligned segments, while Code-21 center-line and deprecated Code-22 lower-left rectangles preserve arbitrary primitive rotation; intrinsic macro orientation composes with LM/LR/LS and supported whole-image IR, with non-orthogonal material flashes/draws emitted as exact polygonal rectangle geometry.

- Added exact production reduction for single positive origin-centered Gerber aperture-macro Polygon primitives (Code 5) to standard `P` apertures. The supported subset enforces integer vertex counts 3–12, positive circumscribed diameter, finite rotation, active-unit conversion, strict/preflight fail-closed validation, and reuses the existing exact P flash/D01/transform/LPD-LPC paths.

- Hardened deprecated Gerber IP image-polarity handling: `%IPPOS*%` is now a once-only image-header command that must precede coordinate data, with explicit positive-polarity diagnostics and preflight coverage. Late or duplicate IPPOS declarations fail closed and suppress permissive geometry; `%IPNEG*%` remains fail-closed because whole-image inversion is not modeled. Also synchronized LPC capability text with the already-supported standard P aperture paths.

- Extended standard P aperture support to solid linear D01 draws on material layers. Because the regular polygon aperture is convex, PHOTONX materializes the exact swept image as the convex hull of the transformed aperture at the segment endpoints, preserving template rotation, LM-before-LR, LS, whole-image IR, step-repeat, provenance and ordered LPD/LPC composition. Holed P D01 remains fail-closed.

- Added bounded standard P regular-polygon aperture support for D03 flashes. P apertures validate outer diameter, integer vertex count 3–12, optional template rotation, and optional centered round hole; LM mirroring is applied before LR, with LS, whole-image IR, step-repeat and ordered LPD/LPC composition preserved. Polygon outer boundaries are exact CopperRegion geometry, while optional round holes retain the 0.005 mm chord-error policy. Holed P-aperture D01 remains explicitly fail-closed; solid P D01 is supported by the exact sweep path above.

- Added specification-compliant zero-diameter standard C aperture support. C0 D01/D03/G02/G03 objects are accepted as legal no-image operations, emit no copper/outline geometry, preserve modal/current coordinate progression, and remain preflight-safe. Arc geometry is still validated before a zero-width arc is treated as image-empty.

- Added bounded support for one centered round-hole modifier on standard C/R/O D03 flashes. Holed flashes are materialized as CopperRegion polygons whose interior ring is transparent within that flash operation, preserving Gerber semantics under dark/clear composition rather than converting the hole into a destructive clear operation. LR/LS, whole-image IR, step-repeat, provenance, connectivity and DRC remain supported. Invalid/non-fitting holes plus holed D01/G02/G03 draws remain fail-closed.

- Added arbitrary finite `LR` support for rectangular and obround D03 flashes on material layers. Orthogonal cases remain PadCandidate objects; non-orthogonal flashes are materialized as CopperRegion polygons so exact rectangular geometry and 0.005 mm chord-error-bounded obround geometry can participate in step-repeat, whole-image transforms, connectivity/DRC, provenance, and ordered LPD/LPC composition without suppressing the file.

- Extended rectangular and obround linear D01 sweeps to arbitrary finite Gerber `LR` rotation. Rotated rectangular sweeps remain polygon-exact; obround curved boundaries retain the 0.005 mm chord-error policy. Effective aperture rotation composes with whole-image `IR`, is recorded in provenance, and participates in LPD/LPC composition. Non-circular Edge.Cuts draws remain fail-closed.

- Added bounded linear D01 support for rectangular and obround Gerber apertures on material layers. Rectangular sweeps are materialized exactly as deterministic CopperRegion polygons; obround sweeps use the existing 0.005 mm inscribed-chord policy for curved aperture boundaries. The geometry participates in step-repeat, supported MI/SF/OF/IR and LM/LR/LS transforms, ordered LPD/LPC image composition, connectivity, DRC, validation, and component-local provenance. Non-circular Edge.Cuts draws remain fail-closed.

- Extended bounded Gerber `%LPC*%` composition to tessellated G02/G03 circular-aperture tracks. Existing 0.005 mm centerline chord-error tessellation is composed with 0.005 mm capsule-cap polygonization and recorded with a conservative <=0.010 mm combined boundary-error budget; arc and track evidence remain component-local and source-ordered. Outline geometry remains fail-closed.

- Extended bounded Gerber `%LPC*%` composition to linear D01 tracks drawn with circular apertures. Linear strokes are materialized as deterministic capsule polygons with exact straight sides and 0.005 mm chord-error-bounded round end-caps, with `gerber_track_polygonization` evidence on affected output components. Source-order dark/clear semantics, step-repeat, transforms, and causal provenance are preserved; tessellated G02/G03 arc tracks and outlines remain fail-closed.

- Hardened LPC composition provenance and stable IDs with ordered effective-contribution tracing. Dark operations now contribute only newly added material that survives later clears; clear operations contribute only newly created boundary that survives on a final component. Redundant dark operations, clear-before-dark no-ops, duplicate clears, and fully erased material no longer contaminate component provenance or rename unchanged composed regions.

- Extended bounded Gerber `%LPC*%` composition to solid circular and obround D03 flashes. C/O boundaries are converted to deterministic symmetric inscribed-chord polygons using the existing 0.005 mm Gerber chord-error policy, with `gerber_flash_polygonization` evidence on affected output components; rectangular flashes remain exact, ordering/refill/preflight semantics are preserved, and tracks/outlines remain fail-closed.

- Extended bounded Gerber `%LPC*%` image composition beyond region-only files to include rectangular D03 flashes. Supported regions and R flashes now share one ordered dark/clear operation stream and materialize to deterministic CopperRegion shells/holes; clear-before-dark, dark refill, mixed region/flash ordering, and step-repeat are covered. Circular/obround flashes, tracks, and outlines remain fail-closed.

- Hardened bounded Gerber LPC materialization so each composed CopperRegion carries only the dark/clear region provenance and LP graphics-state sources that geometrically contribute to that final component. Unrelated disjoint operations no longer contaminate component provenance or stable IDs, while point-only clear contact is treated as a no-op dependency.

- Added bounded Gerber `%LPC*%` parser support for region-only files. Supported G36/G37 CopperRegion operations now retain source order across LPD/LPC switches, compose through exact polygon union/difference, and materialize deterministic shells/holes with composition provenance; clear-before-dark, dark-after-clear refill, split components, and preflight are covered. Any LPC file containing tracks, flashes, or outline material geometry remains fail-closed and suppresses the complete permissive file image.

- Added deterministic ordered Gerber polygon image composition on top of the image-operation stream: dark Polygon/MultiPolygon operations union into accumulated material, clear operations subtract only from material already present, invalid/non-polygonal geometry and sequence gaps fail closed, and composed shells/holes are canonicalized for stable downstream materialization. This engine is now used by the bounded region-only LPC parser subset described above.

- Extended Gerber cut-in reconstruction from one hole to multiple holes per contour. Every fully-coincident opposite linear bridge pair is removed to recover closed boundary cycles; all cut-ins must share one axis direction, hole rings must be strictly contained, non-touching, non-nested, and opposite-wound relative to the shell, and each bridge may contact contour boundaries only at its endpoints. Disjoint top-level cut-in topology remains fail-closed.

- Added bounded Gerber cut-in hole reconstruction: fully-coincident opposite horizontal/vertical linear bridge pairs are decomposed into an outer shell plus explicit hole geometry. Linear and G75 circular inner boundaries are supported; hole geometry propagates through image transforms, step-repeat, connectivity, DRC, validation, serialization, and roundtrip canonicalization with explicit gerber_region_cut_in provenance.

- Added dark G36/G37 multi-contour region support: each D02 starts a contour, a new D02 finalizes the previous contour only when explicitly closed, coordinate-free D02 starts at the current point, and each valid contour is emitted as deterministic copper geometry with statement-level union semantics. Overlapping and touching contours remain valid.

- Added G75 multi-quadrant G02/G03 circular boundaries inside dark single-contour G36/G37 regions with deterministic 0.005 mm output chord-error-bounded tessellation, incremental endpoint support, anisotropic SF-compatible boundary transforms, and explicit arc provenance; G74 region arcs are now supported within the same bounded single-quadrant rules.
- Corrected region closure semantics to match the Gerber specification: G37 no longer implicitly closes an open contour, and zero-length contour segments are rejected.

- Added bounded dark Gerber G36/G37 region reconstruction as copper polygons, initially for single linear contours and later extended to G75 circular boundaries, multiple contours, and bounded simple cut-in holes; complex/disjoint or mixed-axis cut-ins, clear-polarity, and Edge.Cuts regions remain fail-closed.
- Hardened legacy Gerber header placement: AS/IN/MI/SF/OF/IR commands are now considered late after the first coordinate statement, including non-emitting D02 moves, rather than only after physical geometry has already been emitted.
- Preflight now classifies LATE_GERBER_* and DUPLICATE_GERBER_* diagnostics as strict blockers so parser-invalid header state cannot be reported as ready for strict reconstruction.
- Expanded production Gerber aperture-transform support from identity-only to an exact modal LM/LR/LS subset: mirror-symmetric C/R/O apertures accept all LM states, circles accept arbitrary finite LR, rectangular/obround flashes accept 90-degree-step LR, and positive LS scales flash dimensions plus circular draw/arc widths. Non-orthogonal R/O flashes remain fail-closed.
- Aperture transform state is applied to the original aperture at object creation (not cumulatively), recorded as provenance, and included in deterministic IDs.
- Corrected Gerber arc provenance under legacy image transforms: reflecting exactly one MI axis now reports the transformed output arc direction as the opposite of the source CW/CCW command, while two-axis mirroring, positive SF, OF translation, and IR rotation preserve orientation. Arc evidence now records both source and output directions.
- Added legacy Gerber `SF` coordinate scaling for the specification range 0.0001..999.99999. SF scales coordinate data only; apertures and step-repeat distances remain unchanged. Uniform scaling is supported for circular interpolation with output-space chord-error preservation, while anisotropic circular interpolation fails closed instead of being approximated as an ellipse.
- Added `gerber_scale_factor` provenance and transform-aware stable-ID inputs for non-identity SF state.
- Added legacy non-geometric Gerber compatibility: both AS axis-select forms are accepted without changing CAD-to-CAM geometry, IN/LN names are preserved as comment diagnostics, G55 and M01 are accepted as no-ops, and M00 now terminates parsing like M02.
- Hardened Gerber end-of-file handling so M02 stops parsing immediately instead of allowing trailing statements to leak geometry after the formal program end.
- Added exact deprecated Gerber `OF` image translation using active MO units, with deterministic composition after MI/SF and before IR regardless of command appearance; translations propagate through flashes, tracks, outlines, tessellated arcs, and step-repeat instances with provenance and transform-aware stable IDs.
- Added exact deprecated Gerber `MI` mirror-image support for A/B coordinate data, preserving the specification rule that apertures and step-repeat distances are not mirrored; MI composes deterministically before IR and is recorded in provenance.
- Included active MI/IR image-transform semantics in generated track/pad/arc stable IDs so geometrically different transformed objects cannot retain the same deterministic ID.
- Added exact deprecated Gerber whole-image `IR` rotation for 0/90/180/270 degrees, applied to flashes, linear draws, outlines, tessellated arcs, incremental-coordinate geometry, and step-repeat instances with explicit provenance evidence.
- Recognized legacy Gerber `SF` scale-factor commands explicitly: identity scaling is accepted, while non-identity or malformed scaling fails closed and suppresses permissive geometry instead of being ignored as an unknown statement.
- Verified PR #54 change set (merged as `8ba238d`) on Python 3.11, 3.12, and 3.13 with 855 passing tests and 2 existing collection warnings (GitHub Actions run `35431302455`).
- Added exact deprecated Code-22 lower-left Gerber macro reduction for positive-size rectangles centered on the macro origin, including 0/90/180/270-degree rotations; non-centered, non-orthogonal, zero-size, and exposure-off cases remain fail-closed.
- Expanded exact rectangular macro normalization so centered Code-20/Code-2 vector-line and Code-21 center-line primitives accept 90-degree-step rotations, and origin-centered circles accept rotation as a geometry-invariant parameter.
- Added exact reduction of single positive origin-centered, axis-aligned Code-20 vector-line Gerber macros (plus the deprecated Code-2 alias) to rectangular apertures; diagonal, offset, non-orthogonally rotated, zero-width, and zero-length cases remain fail-closed.
- Added legacy Gerber incremental coordinate support for `G91` and FS `I` notation: X/Y values now accumulate from the preceding coordinate position, `G90`/FS `A` restore absolute notation, and arc I/J values remain center offsets from the arc start.
- Added exact reduction of single positive origin-centered, zero-rotation Code-21 center-line Gerber macros to rectangular apertures, with active-unit conversion and fail-closed boundaries.
- Hardened Gerber unit semantics: dimensional data now requires explicit `MO` or supported legacy `G70/G71`, and conflicting unit switches fail closed with permissive file-geometry suppression instead of defaulting to millimeters or mixing unit systems.
- Verified merged commit `ec8383b` on Python 3.11, 3.12, and 3.13 with 824 passing tests and 2 existing collection warnings (GitHub Actions run `35427167859`).
- Hardened Gerber step-and-repeat state handling so malformed, non-positive, or over-limit `%SR...%` commands suppress permissive file geometry instead of falling back to a single un-repeated copy.
- Hardened Excellon linear-route and G85 failure handling so malformed commands, invalid routing state transitions, empty route termination, and unterminated routes suppress permissive file geometry instead of allowing partial routes or mixed drill/slot output.
- Verified merged commit `de1a6a2` on Python 3.11, 3.12, and 3.13 with 778 passing tests and 2 existing collection warnings.
- Hardened Excellon routed-arc failure handling so unsupported syntax, missing centers, invalid arc geometry, or invalid route state suppresses permissive file geometry instead of allowing an incomplete route to be emitted; invalid arc geometry is now a strict preflight blocker.
- Rejected zero-diameter Excellon tools and suppressed permissive file geometry so zero-width drills, slots, or routes cannot enter reconstruction.
- Hardened Excellon unit handling so tool definitions before explicit `METRIC/INCH/M71/M72` units no longer inherit the parser's default millimeter state; permissive parsing suppresses file geometry instead.
- Added legacy Excellon incremental coordinate support for `G91` and `ICI,ON`: drill hits and routed endpoints accumulate from the previous coordinate, G85 slot starts accumulate from the preceding coordinate and slot ends from the slot start, and explicit `G90` / `ICI,OFF` switches back to absolute mode.
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
