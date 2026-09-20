# Package Catalog
Stores package geometry metadata used for footprint-hypothesis matching. Matching by pin count, pitch and mounting technology produces ranked candidates rather than asserting a package identity.

## Geometry evidence

Footprint hypotheses use rotation-tolerant pad topology rather than package names from manufacturing files. Existing exact and row-family signatures keep their current confidence and ambiguity gates. Grid-array SMD hypotheses add an independent lattice fingerprint based on nearest-neighbor directions, grid occupancy, and central symmetry so square BGA/LGA-like pad arrays remain detectable even when principal-axis orientation is degenerate.

`GRID_ARRAY_SMD` requires at least a 3×3 populated grid, high occupancy, SMD-only pad evidence, and central symmetry. It remains a generic geometry family only: PhotonX does not infer a manufacturer package, MPN, value, component identity, or missing pins from the fingerprint.
