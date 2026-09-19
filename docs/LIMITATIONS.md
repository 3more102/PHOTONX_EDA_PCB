# Current limitations

PHOTONX 0.2.0 is an engineering reconstruction scaffold, not a complete CAM replacement.

## Implemented now

- strict linear Gerber draws and flashes using C/R/O apertures;
- Gerber step-and-repeat expansion for supported linear geometry, with deterministic IDs and source provenance;
- G75 multi-quadrant G02/G03 circular arcs with signed I/J center offsets and circular draw apertures, tessellated with explicit approximation evidence;
- bounded legacy G74 single-quadrant G02/G03 arcs using unsigned I/J distances when one center candidate is unambiguous and the sweep is at most 90 degrees;
- single positive origin-centered circle aperture macros, including parameterized diameters, reduced exactly to circular apertures; centered-circle rotation is geometry-invariant;
- exact rectangular reduction for centered axis-aligned Code-20 vector-line macros (plus deprecated Code-2 alias) with 90-degree-step rotation;
- single positive Code-21 center-line aperture macros reduced exactly to centered rectangular apertures with 90-degree-step rotation;
- deprecated Code-22 lower-left rectangle macros reduced exactly when their lower-left coordinates place the rectangle center at the macro origin and rotation is in 90-degree steps;
- explicit X2 `.FilePolarity,Positive` metadata is recognized without changing positive-image geometry;
- Gerber `%LPD*%` dark layer polarity is accepted as the supported positive-object state;
- identity Gerber aperture transforms (`%LMN*%`, zero/full-turn `LR`, and `%LS1*%`) are accepted;
- deprecated `MI` mirroring is supported exactly for A/B coordinate data, including flashes, linear draws, tessellated arcs, outlines, and incremental coordinates; apertures and step-repeat distances are intentionally not mirrored;
- deprecated `OF` translation is supported exactly in the active MO units, including flashes, linear draws, arcs, outlines, and step-repeat instances, and composes after MI/SF and before IR;
- both legacy `ASAXBY` and `ASAYBX` are accepted as output-device-only metadata because AS does not affect CAD-to-CAM image geometry;
- legacy `IN` and `LN` names are retained as comment diagnostics, `G55` and `M01` are accepted as no-ops, and `M00` terminates parsing with the same stop semantics as `M02`;
- deprecated whole-image `IR` rotation is supported exactly for its specification-defined 0/90/180/270-degree values, including flashes, linear draws, tessellated arcs, outlines, and step-repeat instances;
- legacy `SF` is recognized explicitly: identity scaling is accepted, while non-identity scaling fails closed;
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

- ambiguous/invalid G74 center cases and complex aperture macros; Gerber regions and aperture blocks are rejected in strict mode and suppress file geometry in permissive mode so their bodies cannot leak as ordinary tracks/flashes;
- standard C/R/O apertures with round-hole modifiers, because aperture-hole image subtraction is not yet represented by the reconstruction model;
- linear D01 draws with rectangular or obround apertures, because PHOTONX does not flatten their swept geometry into an incorrect width-only track;
- X2 `.FilePolarity,Negative` image inversion: strict mode rejects it, while permissive mode records the unsupported semantic and suppresses all geometry from that file rather than treating clearances as positive material;
- Gerber `%LPC*%` clear layer polarity: strict mode rejects it, while permissive mode suppresses the file geometry because clear objects subtract from previously created image content and object ordering matters;
- non-identity Gerber aperture mirroring/rotation/scaling (`LM/LR/LS`): strict mode rejects them, while permissive mode suppresses file geometry because these graphics-state transforms alter flashes, draws, and arcs;
- unsupported legacy Gerber `IP/SF` semantics: strict mode rejects them and permissive mode suppresses file geometry rather than emitting incorrect image semantics; `AS` is output-device-only and `MI`, `OF`, and `IR` are modeled within their declared subsets;
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
