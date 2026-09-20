# Current limitations

PHOTONX 0.2.0 is an engineering reconstruction scaffold, not a complete CAM replacement.

## Implemented now

- strict linear Gerber draws and flashes using C/R/O apertures;
- Gerber step-and-repeat expansion for supported linear geometry and regions, with deterministic IDs and source provenance;
- Gerber G36/G37 region statements with multiple explicitly closed contours, linear segments, bounded G74 single-quadrant and G75 multi-quadrant G02/G03 circular boundaries, and multiple cut-in holes per contour when every bridge is a fully-coincident opposite horizontal/vertical linear pair and all cut-ins in that contour share one axis direction. Files containing supported regions, C/R/O/P D03 flashes including supported round-hole variants, valid general Code-4 outline-macro D03 flashes, linear C/R/O/P D01 aperture sweeps, and circular-aperture G02/G03 tracks may switch between LPD/LPC; R flashes, region boundaries, and rectangular linear sweeps are exact, while C/O curved boundaries use deterministic inscribed chords with explicit provenance and a 0.005 mm maximum chord-error target; ordered clear subtraction is materialized as first-class CopperRegion shells/holes that participate in connectivity, DRC, validation, supported whole-image transforms, step-repeat expansion, roundtrip canonicalization, provenance, and explicit KiCad-export omission reporting. Circular boundaries are deterministically tessellated to a 0.005 mm maximum output chord-error target;
- G75 multi-quadrant G02/G03 circular arcs with signed I/J center offsets and circular draw apertures, tessellated with explicit approximation evidence;
- bounded legacy G74 single-quadrant G02/G03 arcs using unsigned I/J distances when one center candidate is unambiguous and the sweep is at most 90 degrees;
- single positive origin-centered circle aperture macros, including parameterized diameters, reduced exactly to circular apertures; Code-1 reduction requires exactly four or five finite modifiers and finite active-unit conversion, while centered-circle rotation is geometry-invariant;
- aperture-macro local `$n=expression` definitions are evaluated in source order from AD-supplied variables; undefined variables evaluate to zero and redefinition of an AD-supplied or previously defined macro variable is rejected as an invalid file;
- exact rectangular reduction for centered non-zero Code-20 vector-line macros (plus deprecated Code-2 alias), including arbitrarily oriented segments and arbitrary finite primitive rotation;
- single positive Code-21 center-line aperture macros reduced exactly to centered rectangular apertures with arbitrary finite primitive rotation;
- deprecated Code-22 lower-left rectangle macros reduced exactly when their lower-left coordinates place the rectangle center at the macro origin, with arbitrary finite primitive rotation;
- intrinsic rectangular macro rotation is preserved through supported LM/LR/LS aperture transforms and whole-image IR; non-orthogonal material flashes/draws use exact polygonal rectangle geometry rather than axis-aligned approximation;
- single positive Code-4 outline macros use exact R/P reduction when the contour is a centered rectangle or centered regular polygon, while other valid explicitly closed simple contours with 3–5000 vertices are retained as exact linear CopperRegion geometry for D03 flashes on material layers. Irregular, concave, and off-center flashes preserve primitive rotation plus LM/LR/LS, supported whole-image IR, step-repeat, provenance, and LPD/LPC. Zero-length, self-touching, self-intersecting, open, off-exposure, or zero-area contours remain fail-closed, as do general Code-4 D01 sweeps and Edge.Cuts flashes;
- single positive Code-5 polygon macros are reduced exactly to standard P apertures when they use an integer 3–12 vertex count, are centered at the macro origin, have positive circumscribed diameter, and finite rotation;
- explicit X2 `.FilePolarity,Positive` metadata is recognized without changing positive-image geometry;
- generic X2 `TF`/`TA`/`TO`/`TD` commands are grammar-validated; tracked `TA`/`TO` state follows Gerber's single name-keyed dictionary semantics, supported `AD` apertures freeze the current `TA` snapshot, geometry created with those apertures carries the frozen metadata as provenance, and `G36` regions snapshot current `TA` state rather than inheriting attributes from the selected aperture. `TD` changes only future tracked state. `.AperFunction` is preserved as source evidence only and is not promoted into component, electrical, or design-intent semantics. Current `TO` object-attribute state is snapshotted onto each subsequently created graphical object's provenance, `TD` deletion is non-retroactive, and `.N` values are preserved as source net-name evidence. Physical nets receive a `.N` label only when the source name is non-reserved, internally consistent, and unique across reconstructed physical groups; empty `.N`, `N/C`, conflicting names, and duplicate names remain explicit unresolved evidence. Standard-name domains, Unicode escapes, reserved characters, attribute names, required `TO.C`/`TO.N` value fields, and attribute commands inside regions fail closed when malformed;
- Gerber `%LPD*%` dark layer polarity is accepted as the supported positive-object state;
- modal Gerber aperture transforms are supported for the representable subset: LM on centered symmetric C/R/O apertures, arbitrary LR on circles and R/O linear D01 sweeps/flashes, and positive LS scaling on supported object geometry; orthogonal R/O flashes remain PadCandidate objects while non-orthogonal flashes are materialized as CopperRegion polygons;
- deprecated `MI` mirroring is supported exactly for A/B coordinate data, including flashes, linear draws, tessellated arcs, outlines, and incremental coordinates; apertures and step-repeat distances are intentionally not mirrored;
- deprecated `SF` coordinate scaling is supported for flashes and linear geometry with independent A/B factors in the specification range; apertures and step-repeat distances remain unscaled, uniform SF supports circular arcs, and anisotropic SF arcs fail closed because they become non-circular;
- deprecated `OF` translation is supported exactly in the active MO units, including flashes, linear draws, arcs, outlines, and step-repeat instances, and composes after MI/SF and before IR;
- both legacy `ASAXBY` and `ASAYBX` are accepted as output-device-only metadata because AS does not affect CAD-to-CAM image geometry; AS/IN/MI/SF/OF/IR header commands must precede the first coordinate statement, including non-emitting D02 moves;
- legacy `IN` and `LN` names are retained as comment diagnostics, `G55` and `M01` are accepted as no-ops, and `M00` terminates parsing with the same stop semantics as `M02`;
- deprecated whole-image `IR` rotation is supported exactly for its specification-defined 0/90/180/270-degree values, including flashes, linear draws, tessellated arcs, outlines, and step-repeat instances;
- metric/inch units and coordinate formats for the supported subset;
- legacy Gerber absolute (`G90` / FS `A`) and incremental (`G91` / FS `I`) X/Y coordinate notation, with I/J retained as arc-center offsets;
- point Excellon drill hits in absolute or incremental (`G91` / `ICI,ON`) coordinate mode;
- Excellon G85 straight slots in absolute or incremental mode, with the incremental start relative to the preceding coordinate and the incremental end relative to the slot start;
- Excellon linear-route and supported routed-arc endpoints in absolute or incremental coordinate mode, while I/J remain arc-center offsets;
- Excellon routed arcs using I/J center offsets and standard XNC X/Y/A radius form, tessellated with explicit approximation evidence;
- deterministic source provenance;
- geometry-based same-layer connectivity;
- physical-net groups;
- conservative component hypotheses;
- validation and JSON reports;
- experimental KiCad board export;
- model-backed Tkinter evidence viewer.

## Deliberately rejected instead of faked

- ambiguous/invalid G74 center cases and complex aperture macros; mixed-axis or otherwise invalid cut-ins, fully-coincident cut-ins that resolve to disjoint filled areas, LPC files containing outline material geometry, plus Edge.Cuts regions and aperture blocks, remain fail-closed rather than being approximated or leaked as ordinary geometry;
- standard C/R/O apertures and standard P regular-polygon apertures (3–12 vertices) with an optional single centered round-hole modifier are supported for D03 flashes on material layers, including LM/LR/LS, supported whole-image IR, step-repeat, and ordered LPD/LPC composition. The hole is represented as transparent geometry inside the flash operation, not as a separate clear operation. The Gerber-defined zero-diameter C aperture is accepted and its D01/D03/G02/G03 objects are treated as no-image operations while preserving coordinate/modal progression. solid P-aperture D01 draws are supported as exact convex sweeps on material layers; holed P D01, other holed D01 linear draws, holed G02/G03 interpolation, non-fitting/zero-size holes, and P/holed Edge.Cuts geometry remain fail-closed;
- X2 `.FilePolarity,Negative` image inversion: strict mode rejects it, while permissive mode records the unsupported semantic and suppresses all geometry from that file rather than treating clearances as positive material;
- Gerber `%LPC*%` clear layer polarity supports G36/G37 regions, supported C/R/O/P D03 flashes, linear C/R/O/P D01 aperture sweeps, and circular-aperture G02/G03 tracks. Round aperture holes remain transparent inside each flash operation and therefore do not clear earlier dark material by themselves. Rectangular linear sweeps are exact; C/O curved boundaries are polygonized conservatively with a 0.005 mm maximum chord-error target and explicit approximation evidence; outline geometry still causes strict rejection and complete permissive-image suppression rather than partial composition;
- deprecated legacy Gerber `%IPPOS*%` is accepted as the default positive whole-image polarity only once and before coordinate data; duplicate or late IPPOS is invalid and suppresses permissive geometry, while `%IPNEG*%` remains fail-closed because whole-image inversion is not modeled. Anisotropic-SF circular interpolation likewise remains fail-closed; `AS` is output-device-only and `MI`, `SF`, `OF`, and `IR` are modeled within their declared subsets;
- Gerber dimensional data before an explicit `MO/G70/G71` unit declaration, or a later conflicting unit switch: strict mode rejects it and permissive mode clears/suppresses file geometry rather than inheriting the parser's default millimeter state or mixing unit systems;

- invalid Gerber step-and-repeat state (malformed syntax, non-positive counts, or expansion beyond the configured safety limit): strict mode rejects it and permissive mode clears/suppresses file geometry rather than silently treating repeated content as a single instance;
- Excellon tool definitions before explicit `METRIC/INCH/M71/M72` units: strict mode rejects them and permissive mode suppresses file geometry instead of assuming the parser's default millimeter state;
- zero-diameter Excellon tools: strict mode rejects them and permissive mode clears/suppresses file geometry instead of producing zero-width drills, slots, or routes;
- unsupported or geometrically invalid Excellon routed arcs: strict mode rejects them; permissive mode clears/suppresses file geometry so a route cannot be emitted with the failed arc segment silently omitted;
- malformed Excellon linear routes, malformed G85 slots, or invalid route-state transitions (including tool changes, drill hits, G05, empty route termination, or EOF while the tool is down): strict mode rejects them and permissive mode suppresses file geometry rather than emitting partial manufacturing geometry;
- Excellon routed-arc dialects outside the bounded I/J center-offset subset and the standard XNC X/Y/A radius form;
- automatic original net names when source data does not prove them;
- definite component references/values from pad geometry alone;
- plated-vs-non-plated claims without source evidence;
- claims of KiCad validity when `kicad-cli` has not actually run.

Production support should be expanded against the official Ucamco grammar/test corpus rather than by silently accepting unknown statements.
