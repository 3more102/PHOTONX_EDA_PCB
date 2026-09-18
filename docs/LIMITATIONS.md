# Current limitations

PHOTONX 0.2.0 is an evidence-driven PCB reconstruction platform, not a complete CAM replacement, electrical sign-off tool, or fabrication guarantee.

The machine-readable capability list in `src/photonx_eda_pcb/capabilities.py` is the implementation-facing source of truth. This document explains the same boundary in human-readable form.

## Implemented in the production path

- strict Gerber linear draws and flashes using C/R/O apertures;
- metric/inch units and declared coordinate formats for the supported parser subset;
- Excellon point drill hits;
- Excellon G85 straight canned slots with explicit endpoints;
- conservative Excellon linear routing for the supported `G00 -> M15 -> G01... -> M16/M17` sequence;
- deterministic source provenance and stable object IDs;
- geometry-based same-layer copper connectivity;
- physical-net groups;
- evidence-backed multilayer/via-span and plated-slot reasoning where source evidence exists;
- conservative component hypotheses;
- validation, diagnostics, and JSON reporting;
- experimental KiCad board export;
- model-backed Tkinter evidence viewer;
- parser conformance, regression, deterministic-replay, and release-readiness infrastructure.

## Partial or experimental

### Excellon routing

Linear routed tool-center paths are supported only for the declared conservative state sequence. Circular routed arcs using `G02/G03` remain unsupported.

Arbitrary routed paths are not exported to KiCad as equivalent copper/mechanical semantics unless the exporter has an explicitly modeled representation. Unsupported export semantics remain visible as omissions rather than guessed CAD.

### KiCad board export

KiCad board export is experimental. A generated file is not treated as natively valid unless `kicad-cli` is actually available and the validation step succeeds.

### Multilayer reconstruction

PHOTONX contains evidence-backed via-span and plated-slot reasoning, but geometry alone never proves plating or a layer span. Unknown plating/span remains unknown.

## Deliberately rejected or left unresolved instead of faked

- Gerber arcs in the production high-level parser;
- Gerber regions in the production high-level parser;
- Gerber aperture macros, step-repeat, and aperture blocks when exact semantics are not implemented;
- Excellon routed arcs (`G02/G03`);
- automatic original logical net names when manufacturing data does not prove them;
- definite component references, values, or MPNs from pad geometry alone;
- plated-vs-non-plated claims without supporting evidence;
- exact original schematic hierarchy or design intent without independent evidence;
- dielectric/material stack-up properties when absent from the source package;
- original design rules, impedance targets, safety claims, EMC status, regulatory approval, or fabrication approval without authoritative evidence;
- claims of KiCad validity when native validation has not run.

## Parser policy

Unsupported constructs must surface as explicit errors or diagnostics. They must not disappear silently.

Production parser support should be expanded against authoritative format references and regression fixtures. Low-level helper recognition of a construct does not automatically mean that the high-level reconstruction path supports the construct safely.

## Evidence policy

A reconstructed claim should remain in one of these states:

- observed from source;
- deterministically derived;
- inferred with evidence/confidence;
- unresolved/unknown.

Missing source facts do not become known merely because a plausible answer exists.
