# Current limitations

PHOTONX 0.2.0 is an engineering reconstruction scaffold, not a complete CAM replacement.

## Implemented now

- strict linear Gerber draws and flashes using C/R/O apertures;
- Gerber step-and-repeat expansion for supported linear geometry, with deterministic IDs and source provenance;
- G75 multi-quadrant G02/G03 circular arcs with signed I/J center offsets and circular draw apertures, tessellated with explicit approximation evidence;
- bounded legacy G74 single-quadrant G02/G03 arcs using unsigned I/J distances when one center candidate is unambiguous and the sweep is at most 90 degrees;
- single positive origin-centered circle aperture macros, including parameterized diameters, reduced exactly to circular apertures;
- single positive Code-21 center-line aperture macros reduced exactly to rectangular apertures when centered at the macro origin with zero rotation;
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
- Excellon routed-arc dialects outside the bounded I/J center-offset subset and the standard XNC X/Y/A radius form;
- automatic original net names when source data does not prove them;
- definite component references/values from pad geometry alone;
- plated-vs-non-plated claims without source evidence;
- claims of KiCad validity when `kicad-cli` has not actually run.

Production support should be expanded against the official Ucamco grammar/test corpus rather than by silently accepting unknown statements.
