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

## KiCad export audit report

When `photonx reconstruct ... --kicad` is requested, the CLI writes three KiCad-facing artifacts:

- `reconstructed.kicad_pcb` — the experimental editable board;
- `kicad_export_report.json` — a structured audit of exported/skipped features and exporter warnings;
- `kicad_validation.txt` — the independent `kicad-cli pcb drc` result when the native validator is available.

The JSON report preserves exporter issue severity, code, object ID, message, exported/skipped slot counts and IDs, skipped region IDs, and an `ok` flag. Warnings do not become errors, and omitted or unsupported evidence stays explicit instead of disappearing from the CLI workflow.

## KiCad native validation

`validate_with_kicad_cli()` runs `kicad-cli pcb drc` with a 30-second timeout by default. Callers may override this with the keyword-only `timeout_s` argument. Missing executables, launch failures, and timeouts return an indeterminate `None` validation result with a diagnostic string instead of being reported as successful validation or hanging the reconstruction workflow. Non-positive or non-finite timeout values are rejected.
