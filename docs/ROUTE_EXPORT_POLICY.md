# Routed-path Export Policy

Arbitrary multi-segment Excellon routed paths are preserved in PHOTONX and JSON but are not silently converted into a KiCad oval pad or board outline.

Until an export representation can preserve equivalent semantics, routes appear in an explicit omission manifest with KICAD_ARBITRARY_ROUTE_UNSUPPORTED.
