# KiCad omission manifest

PHOTONX keeps reconstructed geometry explicit when the current KiCad exporter cannot represent it faithfully. The omission manifest is the machine-readable record of what the generated board contains and what it intentionally leaves out.

`export_kicad_with_report()` records export decisions in `KicadExportReport`. `omission_manifest()` exposes these geometry lists:

- `exported_slots`
- `skipped_slots`
- `exported_regions`
- `skipped_regions`
- `exported_tracks`
- `skipped_tracks`
- `omitted_routes`

Every skipped or omitted object must have a matching exporter issue with an approved reason code for that geometry family. `validate_omission_manifest()` checks this invariant, duplicate IDs, and exported/skipped overlap for object families that can be represented conditionally.

Current conservative policies include:

- unknown-plating or unsupported plated slots are skipped;
- valid copper-region shells and holes are exported as editable zone contours; hole-bearing zones omit cached fill and require an explicit KiCad repour, while invalid topology, unsupported layers, and unresolved-net regions are skipped;
- tracks with a non-empty unresolved `net_id` are skipped instead of being relabelled net 0;
- arbitrary Excellon routed paths remain preserved in PHOTONX/JSON but omitted from KiCad.

Older manifests remain readable: missing newer list keys are interpreted as empty lists.
