# Roundtrip Verification

Round-trip verification canonicalizes reconstructed models and compares stable fingerprints/invariants. KiCad textual counts are supplemental and do not replace parsing with a format-aware reader.

The structural board fingerprint covers tracks, pads, drill hits, mechanical slots, Excellon routed paths, copper regions (including region holes), board outline geometry, and reconstructed physical nets. Collections are canonicalized by stable object ID so input ordering does not change the fingerprint.

Routed paths are fingerprinted from their ordered point sequence, width, plating state, and tool identity. This prevents route loss or route-geometry changes from being invisible to deterministic replay and release-evidence checks.

The structural fingerprint intentionally does not treat provenance records, parser diagnostics, metadata, or component hypotheses as physical-geometry equivalence.
