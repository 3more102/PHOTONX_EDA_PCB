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
- standalone D01/D02/D03 modal operation selection;
- legacy G70/G71 unit selection and explicit G90 absolute mode;
- identity legacy Gerber transform statements;
- Excellon M71/M72 metric/inch selection;
- Excellon tool definitions with feed/spindle suffixes;
- additional Protel/Altium/EAGLE-style layer/file extensions;
- headerless Excellon-like packages are detected, but PHOTONX will not silently
  guess their units;
- simple parameterized Gerber aperture macros that resolve to one positive,
  centered circle are accepted as exact circular apertures;
- legacy Gerber G74 single-quadrant arcs are accepted only when unsigned I/J
  distances resolve to one unambiguous center with a sweep of at most 90 degrees.

Discovery reads only a bounded prefix of each candidate file rather than loading
entire files into memory. Binary-looking files containing NUL bytes in the
sniff window are ignored by content detection.

### Fail-closed boundaries

PHOTONX still rejects or explicitly diagnoses semantics that would be unsafe to
guess, including Gerber G91 incremental coordinates, non-identity legacy
transforms, Gerber regions/complex aperture macros not supported by the production
geometry path, aperture blocks, and Excellon routed-arc dialects outside the bounded G02/G03 I/J subset. An input being discovered does not mean
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
