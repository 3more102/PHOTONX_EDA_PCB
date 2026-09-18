# Footprint Spatial Clustering

Pad clustering now uses radius-neighbor queries and deterministic breadth-first connected components rather than repeatedly scanning every remaining pad.

This preserves the existing proximity-clustering semantics. It does not solve the broader semantic problem of separating adjacent unrelated components.
