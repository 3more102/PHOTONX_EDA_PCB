# Exports

Exports include KiCad, JSON, CSV summaries, GraphML connectivity, SVG visualization and source manifests. Export availability does not imply full semantic recovery.

## Reconstruction CLI review exports

`photonx reconstruct` always writes the canonical reconstruction bundle and `reconstructed.json`.

For a cohesive review package, use:

```bash
photonx reconstruct path/to/manufacturing_data \
  --output build/board \
  --review-artifacts
```

This adds:

- `review/report.md` — human-readable reconstruction report and checks;
- `review/summary.json` — machine-readable quality/completeness summary;
- `review/checks.junit.xml` — check findings for CI ingestion;
- `review/board.svg` — lightweight geometry preview;
- `review/connectivity.graphml` — reconstructed physical-net connectivity;
- `review/csv/nets.csv` and `review/csv/components.csv` — tabular review data.

For individually addressable outputs, use `--svg`, `--graphml`, and/or `--csv`:

- `--svg` -> `reconstructed.svg`;
- `--graphml` -> `reconstructed.graphml`;
- `--csv` -> `csv/nets.csv` and `csv/components.csv`.

The bundle and individual flags are additive and may be combined. They do not alter reconstruction semantics, validation severity, or exit-code behavior. The optional `--kicad` flag remains separate because KiCad export has its own conservative omission and native-validation policy.

## KiCad export audit artifacts

When `photonx reconstruct ... --kicad` is requested, the CLI writes five KiCad-facing artifacts:

- `reconstructed.kicad_pcb` — the experimental editable board representation;
- `kicad_export_report.json` — the complete current `KicadExportReport`, including counts, exported/skipped IDs, structured issues, and `ok`;
- `kicad_omissions.json` — the stable omission-manifest view covering slots, copper regions, tracks, and arbitrary routed paths;
- `kicad_connectivity_roundtrip.json` — an immediate export/reload comparison of the net table, exported track bindings, and recovered-pad bindings, with explicit connectivity-loss accounting for skipped tracks and unresolved pad nets;
- `kicad_validation.txt` — the independent native `kicad-cli pcb drc` result when the validator is available.

Exporter warnings and round-trip findings do not change reconstruction exit-code semantics. The connectivity artifact separates `roundtrip_equal` (the re-read KiCad file matches the exporter policy) from `source_equivalent` (no tracked source connectivity was lost). Its current scope is the net table, board track segments, and `PHOTONX:RecoveredPad` footprints; copper-zone and plated-slot connectivity remain outside this validator. The audit files make conservative omissions, defaulted zone rules, omitted fill caches, unresolved references, and export/reload mismatches visible instead of discarding that evidence in the normal CLI workflow.

## KiCad native validation

`validate_with_kicad_cli()` runs `kicad-cli pcb drc` with a 30-second timeout by default. Callers may override this with the keyword-only `timeout_s` argument. Missing executables, launch failures, and timeouts return an indeterminate `None` validation result with a diagnostic string instead of being reported as successful validation or hanging the reconstruction workflow. Non-positive or non-finite timeout values are rejected.
