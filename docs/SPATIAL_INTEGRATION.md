# Spatial Integration

Physical connectivity and copper-clearance DRC now generate candidate pairs through a deterministic spatial hash before performing exact Shapely checks.

Brute-force implementations remain available as reference paths for parity regression tests.

Spatial indexing may reduce pair checks dramatically on sparse boards, but exact geometry remains authoritative.
