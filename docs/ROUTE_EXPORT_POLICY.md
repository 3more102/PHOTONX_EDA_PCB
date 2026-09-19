# Routed-path Export Policy

Arbitrary multi-segment Excellon routed paths are preserved in PHOTONX and JSON but are not silently converted into a KiCad oval pad or board outline.

Until an export representation can preserve equivalent semantics, every routed path is omitted from KiCad output and is recorded by `export_kicad_with_report()` as a warning with `KICAD_ARBITRARY_ROUTE_UNSUPPORTED`.

The unified KiCad omission manifest includes routed-path IDs under `omitted_routes`, alongside skipped slots and unsupported copper regions. This keeps a machine-readable record of geometry intentionally absent from the generated `.kicad_pcb` file.
