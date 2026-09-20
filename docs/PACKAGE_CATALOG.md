# Package Catalog

Stores package geometry metadata used for footprint-hypothesis matching. Matching by pin count, pitch, mounting technology, row/grid structure, rotationally normalized geometry, and central symmetry produces ranked candidates rather than asserting a package identity.

Exact legacy signatures (for example `TWO_PIN_THT`, `SOIC8_LIKE`, and `DIP8_LIKE`) retain their existing scoring behavior. Generic families such as `DUAL_ROW_THT_LIKE`, `DUAL_ROW_SMD_LIKE`, and `GRID_ARRAY_SMD_LIKE` are geometry-gated and capped below valid exact-signature confidence.

Matching is fail-closed: if every signature scores zero, the matcher returns `best=None` and `confidence=0.0` instead of inventing a package hypothesis.
