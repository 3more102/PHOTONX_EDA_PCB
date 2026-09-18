# Current limitations

PHOTONX 0.2.0 is an engineering reconstruction scaffold, not a complete CAM replacement.

## Implemented now

- strict linear Gerber draws and flashes using C/R/O apertures;
- Gerber step-and-repeat expansion for supported linear geometry, with deterministic IDs and source provenance;
- G75 multi-quadrant G02/G03 circular arcs with signed I/J center offsets and circular draw apertures, tessellated with explicit approximation evidence;
- bounded legacy G74 single-quadrant G02/G03 arcs using unsigned I/J distances when one center candidate is unambiguous and the sweep is at most 90 degrees;
- single positive centered-circle aperture macros, including parameterized diameters, reduced exactly to circular apertures;
- explicit X2 `.FilePolarity,Positive` metadata is recognized without changing positive-image geometry;
- Gerber `%LPD*%` dark layer polarity is accepted as the supported positive-object state;
- metric/inch units and coordinate formats for the supported subset;
- point Excellon drill hits;
- Excellon routed arcs using I/J center offsets and standard XNC X/Y/A radius form, tessellated with explicit approximation evidence;
- deterministic source provenance;
- geometry-based same-layer connectivity;
- physical-net groups;
- conservative component hypotheses;
- validation and JSON reports;
- experimental KiCad board export;
- model-backed Tkinter evidence viewer.

## Deliberately rejected instead of faked

- ambiguous/invalid G74 center cases, Gerber regions, complex aperture macros, and aperture blocks;
- standard C/R/O apertures with round-hole modifiers, because aperture-hole image subtraction is not yet represented by the reconstruction model;
- linear D01 draws with rectangular or obround apertures, because PHOTONX does not flatten their swept geometry into an incorrect width-only track;
- X2 `.FilePolarity,Negative` image inversion: strict mode rejects it, while permissive mode records the unsupported semantic and suppresses all geometry from that file rather than treating clearances as positive material;
- Gerber `%LPC*%` clear layer polarity: strict mode rejects it, while permissive mode suppresses the file geometry because clear objects subtract from previously created image content and object ordering matters;
- Excellon routed-arc dialects outside the bounded I/J center-offset subset and the standard XNC X/Y/A radius form;
- automatic original net names when source data does not prove them;
- definite component references/values from pad geometry alone;
- plated-vs-non-plated claims without source evidence;
- claims of KiCad validity when `kicad-cli` has not actually run.

Production support should be expanded against the official Ucamco grammar/test corpus rather than by silently accepting unknown statements.
