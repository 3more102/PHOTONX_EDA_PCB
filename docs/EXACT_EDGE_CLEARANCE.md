# Exact Edge Clearance

DRC now constructs the reconstructed outline boundary and measures exact Shapely distance from track/pad copper geometry to that boundary.

It reports:
- BOARD_OUTLINE_MISSING when no outline exists;
- BOARD_OUTLINE_NOT_CLOSED when no closed outer polygon can be formed;
- COPPER_EDGE_CLEARANCE for copper inside the outer polygon but below the configured clearance;
- COPPER_OUTSIDE_BOARD for copper extending outside the reconstructed outer polygon.

Current outside detection uses the largest closed polygon as the outer board boundary. Complex internal cutouts require additional hierarchy semantics; their boundary lines still participate in distance calculations.
