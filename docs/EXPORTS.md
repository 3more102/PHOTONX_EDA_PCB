# Exports

Exports include KiCad, JSON, CSV summaries, GraphML connectivity, SVG visualization and source manifests. Export availability does not imply full semantic recovery.

## Reconstruction CLI exports

`photonx reconstruct` always writes the canonical reconstruction bundle and `reconstructed.json`. Optional review-oriented exports can now be requested directly from the same reconstruction run:

```bash
photonx reconstruct path/to/manufacturing_data \
  --output build/board \
  --svg \
  --graphml \
  --csv
```

This adds:

- `reconstructed.svg` — lightweight geometry visualization for human review.
- `reconstructed.graphml` — physical-net membership graph for graph tooling.
- `csv/nets.csv` and `csv/components.csv` — tabular summaries for review and downstream analysis.

The optional `--kicad` flag remains separate because KiCad export has its own conservative omission and native-validation policy.
