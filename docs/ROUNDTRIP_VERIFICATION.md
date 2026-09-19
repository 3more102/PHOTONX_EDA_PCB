# Roundtrip Verification

Round-trip verification canonicalizes reconstructed models and compares stable fingerprints/invariants. KiCad textual counts are supplemental and do not replace parsing with a format-aware reader.

## KiCad connectivity readback

When KiCad export is requested, PHOTONX can parse its generated `.kicad_pcb` back through the KiCad reader and compare electrical semantics against the exact exporter report.

The connectivity audit covers:

- the KiCad net table;
- exported track net bindings;
- recovered-pad net bindings by preserved PHOTONX reference identity;
- exported copper-region zone net bindings by `PHOTONX:<region-id>` identity;
- recovered NPTH/plated-slot footprint net bindings by preserved PHOTONX reference identity.

The result distinguishes three conditions:

- `roundtrip_equal`: the objects the exporter reported as emitted re-read with the same connectivity semantics;
- `source_connectivity_complete`: the export did not omit connectivity-bearing source objects or suppress unresolved pad/slot net references;
- `source_equivalent`: both conditions above are true.

Conservative exporter omissions remain explicit losses rather than being misreported as parser/readback corruption. A successful connectivity round-trip does not prove recovery of the original schematic and does not replace native `kicad-cli pcb drc` validation.
