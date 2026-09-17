# Data model

## Physical objects

- `Track`: line segment, width, layer, provenance, physical-net back reference.
- `PadCandidate`: flashed aperture geometry; it becomes a candidate pad, not a proven component pin.
- `DrillHit`: point drill with diameter and tool. Plating defaults to `unknown` unless evidence proves otherwise.
- `OutlineSegment`: recovered Edge.Cuts geometry.

## Reconstructed objects

- `NetGroup`: geometry-connected physical island with confidence and evidence.
- `ComponentHypothesis`: grouping of pad candidates; stores kind, confidence and human-readable evidence.

## Provenance

Every parsed physical object keeps its source file and source line. Inference adds evidence rather than overwriting source truth.

## Deterministic IDs

IDs are content-derived, making repeated runs diffable and suitable for regression tests.
