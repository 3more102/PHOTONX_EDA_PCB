# Routed-path Export Policy

Arbitrary multi-segment Excellon routed paths are preserved in PHOTONX and JSON but are not silently converted into a KiCad oval pad or board outline.

Until an export representation can preserve equivalent semantics, every routed path is omitted from KiCad output and recorded by `export_kicad_with_report()` with `KICAD_ARBITRARY_ROUTE_UNSUPPORTED`.

The unified KiCad omission manifest exposes these IDs under `omitted_routes`, alongside conditional slot, copper-region, and track export decisions. This keeps a machine-readable record of geometry intentionally absent from the generated `.kicad_pcb` file.
