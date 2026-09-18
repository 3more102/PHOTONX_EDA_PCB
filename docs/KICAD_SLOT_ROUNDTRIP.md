# KiCad slot round-trip

The KiCad reader now parses round and oval drill definitions without treating the `oval` token as a numeric diameter.

For oval drills it records both dimensions, pad rotation, footprint rotation and drill offset. NPTH oval drills are converted into reconstructed SlotFeature geometry for round-trip comparison.

The comparison is geometric. It does not claim the generated KiCad UUID or footprint identity matches an original design.
