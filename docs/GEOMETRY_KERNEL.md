# Geometry Kernel

Connectivity and DRC now share one geometry implementation.

Supported reconstructed pad shapes:
- C: circular/elliptical geometry;
- R: rectangle;
- O: capsule/oval.

Optional rotation metadata is honored when present. Exact predicates remain Shapely-based.
