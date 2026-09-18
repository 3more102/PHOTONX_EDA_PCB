# Generic manufacturing input

PHOTONX accepts three input shapes through the production reconstruction path:

- a directory containing Gerber/Excellon data;
- a single manufacturing file;
- a ZIP package containing a manufacturing-data tree.

Directory and ZIP discovery is recursive. Detection does not rely only on file
extensions: PHOTONX inspects file content for Gerber/Excellon signatures and
uses Gerber X2 `TF.FileFunction` metadata when available to infer the PCB
layer.

## Preflight

Run a parser-backed compatibility check before reconstruction:

```bash
photonx preflight board.zip
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
