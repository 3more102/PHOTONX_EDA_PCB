# Roundtrip Verification

Round-trip verification canonicalizes reconstructed models and compares stable fingerprints/invariants. KiCad textual counts are supplemental and do not replace parsing with a format-aware reader.

## KiCad connectivity readback

When KiCad export is requested, PHOTONX re-reads the generated `.kicad_pcb` through its KiCad S-expression reader and compares electrical semantics against the exact `KicadExportReport`.

The connectivity audit checks:

- exact declared KiCad layer-table ID/name/type identity, including the contiguous inner-copper prefix and generated user layers;
- exact KiCad net-table code/name identity;
- net bindings on track segments the exporter reported as emitted;
- exact emitted `Edge.Cuts` line geometry/stroke semantics and deterministic outline UUID identity while preserving the legacy `edge_lines` reader surface;
- recovered-pad identity, deterministic footprint/child-pad UUIDs, emitted geometry (position, layer, type, shape, size, angle, drill semantics, and layer set), and net bindings;
- exported copper-region identity, zone net binding, and canonical shell/hole geometry using the existing start/winding-invariant region comparator;
- recovered NPTH/plated-slot identity, kind, net binding, and canonical mechanical geometry using the existing slot round-trip comparator;
- consistency between embedded KiCad net names and the board net table where the file format carries both;
- proven plated via spans that are part of source physical connectivity but are not emitted by the current KiCad exporter.

The JSON result deliberately separates:

- `roundtrip_equal`: emitted KiCad objects re-read with the same supported electrical semantics;
- `source_connectivity_complete`: no connectivity-bearing track, region, slot, proven plated via span, or unresolved pad/slot net claim was lost by conservative export policy;
- `source_equivalent`: both conditions are true.

A skipped source object is therefore recorded as a source-equivalence loss, not mislabeled as readback corruption. Proven plated via spans are listed in `losses.omitted_proven_via_span_drill_ids` and in the omission manifest as `omitted_via_spans`; PHOTONX does not synthesize KiCad via annular geometry when that geometry is not explicitly reconstructed. Conversely, a changed net ordinal, changed embedded net name, missing recovered identity, duplicate net code, or unexpected emitted connectivity fails the round-trip check.

Copper-region shell/hole geometry is also checked independently by `compare_kicad_copper_regions()`. The connectivity audit does not replace native `kicad-cli pcb drc` validation and does not claim recovery of original schematic intent.
