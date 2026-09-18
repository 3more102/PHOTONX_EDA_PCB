# Current limitations

PHOTONX 0.2.0 is an engineering reconstruction scaffold, not a complete CAM replacement.

## Implemented now

- strict linear Gerber draws and flashes using C/R/O apertures;
- Gerber step-and-repeat expansion for supported linear geometry, with deterministic IDs and source provenance;
- G75 multi-quadrant G02/G03 circular arcs with signed I/J center offsets and circular draw apertures, tessellated with explicit approximation evidence;
- bounded legacy G74 single-quadrant G02/G03 arcs using unsigned I/J distances when one center candidate is unambiguous and the sweep is at most 90 degrees;
- single positive centered-circle aperture macros, including parameterized diameters, reduced exactly to circular apertures;
- metric/inch units and coordinate formats for the supported subset;
- point Excellon drill hits;
- deterministic source provenance;
- geometry-based same-layer connectivity;
- physical-net groups;
- conservative component hypotheses;
- validation and JSON reports;
- experimental KiCad board export;
- model-backed Tkinter evidence viewer.

## Deliberately rejected instead of faked

- ambiguous/invalid G74 center cases, Gerber regions, complex aperture macros, and aperture blocks;
- Excellon routed arcs outside the bounded G02/G03 I/J center-offset subset, including radius/A-form dialects;
- automatic original net names when source data does not prove them;
- definite component references/values from pad geometry alone;
- plated-vs-non-plated claims without source evidence;
- claims of KiCad validity when `kicad-cli` has not actually run.

Production support should be expanded against the official Ucamco grammar/test corpus rather than by silently accepting unknown statements.
