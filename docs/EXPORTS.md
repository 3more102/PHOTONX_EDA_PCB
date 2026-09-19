# Exports

Exports include KiCad, JSON, CSV summaries, GraphML connectivity, SVG visualization and source manifests. Export availability does not imply full semantic recovery.

## CLI review bundle

`photonx reconstruct INPUT --output OUTPUT --review-artifacts` emits review-oriented artifacts without changing reconstruction semantics or exit-code behavior:

- `review/report.md` — human-readable reconstruction report and checks
- `review/summary.json` — machine-readable quality/completeness summary
- `review/checks.junit.xml` — check findings for CI ingestion
- `review/board.svg` — lightweight geometry preview
- `review/connectivity.graphml` — reconstructed physical-net connectivity
- `review/csv/nets.csv` and `review/csv/components.csv` — tabular review data

The bundle is additive: canonical `board.json`, `validation.json`, and `reconstructed.json` outputs are unchanged. Experimental KiCad output remains controlled separately by `--kicad`.
