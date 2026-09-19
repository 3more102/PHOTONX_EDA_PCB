# Generic manufacturing input

PHOTONX accepts multiple input shapes through the production reconstruction path:

- a directory containing Gerber/Excellon data;
- a single manufacturing file;
- a ZIP package;
- a TAR package;
- a compressed TAR package such as TAR.GZ or TGZ.

Directory and archive discovery is recursive. Detection does not rely only on file
extensions: PHOTONX inspects file content for Gerber/Excellon signatures and
uses Gerber X2 `TF.FileFunction` metadata when available to infer the PCB
layer.

## Preflight

Run a parser-backed compatibility check before reconstruction:

```bash
photonx preflight board.zip
photonx preflight board.tgz
photonx preflight board.zip --output preflight.json
```

The report lists each discovered manufacturing file, its detected kind, layer,
detection confidence, diagnostics, and strict-mode blockers.

The preflight uses the same production Gerber and Excellon parsers in
permissive mode. This means the result reflects what the current parser path
can actually consume rather than claiming support based only on a filename.

## Reconstruction

```bash
photonx reconstruct board.zip --output out --kicad
photonx reconstruct board.tgz --output out --kicad
```

Strict reconstruction is the default. If preflight finds syntax that the
strict parser would reject, the CLI writes `out/input_preflight.json` and
returns without silently dropping the feature.

For evidence-preserving best-effort processing:

```bash
photonx reconstruct board.zip --output out --kicad --permissive
```

Unsupported or unrecognized constructs remain visible in diagnostics. Unknown
Gerber layer identity is also reported explicitly.

## What "generic input" means

Generic input means the ingestion path is board-independent and can discover
ordinary Gerber/Excellon packages even when directory layout, filenames, or
extensions differ.

It does **not** mean that every historical or vendor-specific RS-274X/XNC
construct is already geometrically implemented. PHOTONX deliberately reports
unsupported constructs instead of inventing geometry or silently ignoring
them.

The target behavior is therefore:

> drop a manufacturing package into PHOTONX -> automatically discover it ->
> reconstruct all supported evidence -> explicitly report every unsupported or
> ambiguous feature.


## Compatibility hardening

The generic input path also handles several common real-world variations:

- Gerber UTF-8 BOMs;
- modal/omitted D01/D02/D03 operation codes after an operation is established;
- specification-defined zero-diameter C apertures as legal no-image objects; D01/D03/G02/G03 commands using them advance parser coordinate state without emitting material geometry;
- standalone D01/D02/D03 modal operation selection;
- legacy G70/G71 unit selection plus modal G90/G91 absolute/incremental coordinate notation;
- deprecated FS `A`/`I` absolute/incremental notation, with X/Y deltas accumulated safely and arc I/J retained as center offsets;
- deprecated Gerber MI mirroring, applied exactly to coordinate data while deliberately leaving apertures and step-repeat distances unmirrored as required by the specification;
- modern Gerber LM/LR/LS aperture graphics-state transforms for the representable subset: C/R/O plus standard P D03 flashes; P polygons honor template rotation and LM-before-LR semantics for D03 and solid linear D01 sweeps, while non-axis-aligned geometry is materialized as CopperRegion polygons rather than forced into PadCandidate;
- deprecated Gerber SF coordinate scaling within the specification range; apertures and step-repeat distances remain unscaled, uniform SF composes with circular arcs, and anisotropic SF arcs fail closed;
- deprecated Gerber OF image translation in the active MO units, applied after MI/SF and before IR regardless of command appearance;
- legacy AS axis-select forms are accepted as output-device-only metadata because they do not alter CAD-to-CAM image geometry; AS/IN/MI/SF/OF/IR header state must appear before the first coordinate statement, including D02 moves;
- legacy IN/LN names are preserved as diagnostic comment metadata; G55 and M01 are accepted as no-image-effect commands, while M00 terminates parsing like M02;
- deprecated whole-image Gerber IR rotation at the specification-defined 0/90/180/270-degree angles, applied exactly to flashes, linear/arc geometry, supported regions, outlines, and step-repeat instances;
- dark G36/G37 Gerber region statements with multiple explicitly closed contours, linear segments plus bounded G74 single-quadrant and G75 multi-quadrant G02/G03 circular boundaries, and multiple cut-in holes per contour when each bridge is a fully-coincident opposite horizontal/vertical linear pair and all bridges in that contour share one axis direction; holes are represented explicitly in CopperRegion geometry and compose with deterministic arc tessellation, supported MI/SF/OF/IR whole-image transforms, and step-repeat;
- Excellon M71/M72 metric/inch selection;
- Excellon tool definitions with feed/spindle suffixes;
- standard XNC G02/G03 routed arcs using explicit X/Y endpoints plus A radius
  (bounded to the <=180-degree semantics defined by XNC);
- additional Protel/Altium/EAGLE-style layer/file extensions;
- headerless Excellon-like packages are detected, but PHOTONX will not silently
  guess their units;
- simple parameterized Gerber aperture macros that resolve to one positive,
  origin-centered circle are accepted as exact circular apertures; circle rotation
  is geometry-invariant when its center is the macro origin;
- single positive Gerber Code-20 vector-line macros (plus deprecated Code-2)
  are accepted when the segment is non-zero and midpoint-centered on the macro origin;
  arbitrary segment orientation and finite primitive rotation are preserved exactly;
- single positive Gerber Code-21 center-line macros are accepted as exact
  rectangular apertures when centered at the macro origin, with arbitrary finite rotation;
- deprecated Gerber Code-22 lower-left rectangles are accepted when positive-size and
  centered on the macro origin by their lower-left coordinates, with arbitrary finite
  primitive rotation;
- single positive Gerber Code-4 outline macros accept the full valid simple linear-contour D03 subset on material layers: 3–5000 vertices, explicit closure, finite coordinates/rotation, no zero-length segments, no self-touching/intersection, and non-zero area. Centered rectangles/regular polygons reuse exact R/P paths; irregular, concave, and off-center outlines are retained as exact CopperRegion flash geometry. General Code-4 D01 sweeps and Edge.Cuts flashes remain fail-closed;
- single positive Gerber Code-5 polygon macros are accepted when they have an integer
  3–12 vertex count, are centered at the macro origin, have a positive circumscribed-circle
  diameter, and use a finite rotation; they reduce exactly to the equivalent standard P aperture;
- legacy Gerber G74 single-quadrant arcs are accepted only when unsigned I/J
  distances resolve to one unambiguous center with a sweep of at most 90 degrees.

Discovery reads only a bounded prefix of each candidate file rather than loading
entire files into memory. Binary-looking files containing NUL bytes in the
sniff window are ignored by content detection.

### Fail-closed boundaries

PHOTONX still rejects or explicitly diagnoses semantics that would be unsafe to
guess, including legacy Gerber IPNEG whole-image inversion (IPPOS is accepted once before coordinate data), anisotropic-SF circular interpolation, unsupported region forms such as disjoint or mixed-axis/invalid cut-in or Edge.Cuts regions, and LPC files that mix clear polarity with outline material geometry (C/R/O/P D03 flashes, including supported single-round-holed variants, and linear C/R/O/P D01 aperture sweeps are supported; round holes are transparent within the flash operation, rectangular sweeps are exact, and C/O curved boundaries use explicitly evidenced 0.005 mm chord-error-bounded polygonization), complex aperture macros, aperture blocks, and Excellon routed-arc dialects outside the bounded G02/G03 I/J or standard XNC X/Y/A-radius subsets. An input being discovered does not mean
every construct inside it is automatically accepted.


## Archive safety

ZIP, TAR, TAR.GZ, and TGZ packages are extracted into temporary private
directories. PHOTONX validates archive members before extraction and rejects:

- path traversal outside the temporary extraction root;
- symbolic and hard links in TAR-family packages;
- device/FIFO special files;
- packages exceeding the configured entry-count limit;
- packages whose declared expanded size exceeds the configured safety limit.

The archive is only a transport container. After extraction, the same recursive
content-aware Gerber/Excellon discovery and preflight path is used.
