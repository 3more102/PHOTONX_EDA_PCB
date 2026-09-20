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
- `kicad_omissions.json` — the stable omission-manifest view covering slots, copper regions, tracks, routed paths, and exported/omitted proven via spans;
- `kicad_connectivity_roundtrip.json` — an immediate export/reload comparison of the net table plus track, recovered-pad, copper-region, and recovered-slot net bindings, with explicit connectivity-loss accounting for conservative omissions and unresolved net claims;
- `kicad_validation.txt` — the independent native `kicad-cli pcb drc` result when the validator is available.

Exporter warnings and round-trip findings do not change reconstruction exit-code semantics. The connectivity artifact separates `roundtrip_equal` (every object the exporter reported as emitted re-reads with the same electrical binding) from `source_connectivity_complete` (no connectivity-bearing source object or net claim was conservatively omitted) and `source_equivalent` (both are true). Its scope covers the net table, board track segments, exactly representable proven plated vias, `PHOTONX:RecoveredPad` footprints, exported `CopperRegion` zones, and recovered NPTH/plated-slot footprints. A proven via is emitted only when it is a full F.Cu↔B.Cu plated span and its complete per-layer circular pad support, common annular diameter, and reconstructed net are all explicit. Partial-layer spans remain audited omissions because the available manufacturing evidence does not prove whether KiCad should model them as blind/buried vias or microvias. CopperRegion shell/hole geometry remains independently checked by `compare_kicad_copper_regions()`. The audit files make conservative omissions, defaulted zone rules, omitted fill caches, unresolved references, and export/reload mismatches visible instead of discarding that evidence in the normal CLI workflow.

## KiCad native validation

`validate_with_kicad_cli()` runs `kicad-cli pcb drc` with a 30-second timeout by default. Callers may override this with the keyword-only `timeout_s` argument. Missing executables, launch failures, and timeouts return an indeterminate `None` validation result with a diagnostic string instead of being reported as successful validation or hanging the reconstruction workflow. Non-positive or non-finite timeout values are rejected.
