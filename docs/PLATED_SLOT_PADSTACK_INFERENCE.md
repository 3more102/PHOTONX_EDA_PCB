# Plated slot pad-stack inference

A slot marked plated is not automatically exportable.

PHOTONX requires:
- explicit plated status;
- copper pads that cover the slot geometry;
- at least two copper layers;
- consistent pad shape and dimensions;
- pad centers aligned with the slot center within tolerance;
- no conflicting physical net IDs;
- currently, an orthogonal slot orientation.

Only then is a simple KiCad plated slotted pad generated.

Different per-layer pad sizes, conflicting nets, one-layer evidence, or non-orthogonal geometry remain unresolved.
