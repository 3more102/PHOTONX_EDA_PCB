# Roundtrip Verification

Round-trip verification canonicalizes reconstructed models and compares stable fingerprints/invariants. KiCad textual counts are supplemental and do not replace parsing with a format-aware reader.

## KiCad connectivity readback

When KiCad export is requested, PHOTONX re-reads the generated `.kicad_pcb` through its KiCad S-expression reader and compares electrical semantics against the exact `KicadExportReport`.

The connectivity audit checks:

- exact KiCad net-table code/name identity;
- net bindings on track segments the exporter reported as emitted;
- recovered-pad identity and net bindings using the preserved `Reference` property;
- exported copper-region identity and zone net bindings using `PHOTONX:<region-id>`;
- recovered NPTH/plated-slot identity, kind, and net binding using the preserved `Reference` property;
- consistency between embedded KiCad net names and the board net table where the file format carries both.

The JSON result deliberately separates:

- `roundtrip_equal`: emitted KiCad objects re-read with the same supported electrical semantics;
- `source_connectivity_complete`: no connectivity-bearing track, region, slot, or unresolved pad/slot net claim was lost by conservative export policy;
- `source_equivalent`: both conditions are true.

A skipped source object is therefore recorded as a source-equivalence loss, not mislabeled as readback corruption. Conversely, a changed net ordinal, changed embedded net name, missing recovered identity, duplicate net code, or unexpected emitted connectivity fails the round-trip check.

Copper-region shell/hole geometry is also checked independently by `compare_kicad_copper_regions()`. The connectivity audit does not replace native `kicad-cli pcb drc` validation and does not claim recovery of original schematic intent.
