# KiCad omission manifest

PHOTONX intentionally omits reconstructed geometry when the current KiCad exporter cannot preserve its semantics faithfully. The omission manifest is the machine-readable record of those decisions.

`export_kicad_with_report()` records omissions in `KicadExportReport`, and `omission_manifest()` exposes four stable geometry lists:

- `exported_slots`: slot IDs represented in the KiCad board;
- `skipped_slots`: slot IDs blocked by plating or pad-stack evidence;
- `skipped_regions`: copper-region IDs omitted because KiCad zone export is not implemented;
- `omitted_routes`: Excellon routed-path IDs omitted because arbitrary routed milling is not yet represented faithfully.

Every skipped or omitted object must also have a corresponding issue entry containing its object ID and reason code. `validate_omission_manifest()` checks that invariant and rejects duplicate IDs inside each manifest category.

Older manifests without `skipped_regions` or `omitted_routes` remain valid; missing keys are interpreted as empty lists.
