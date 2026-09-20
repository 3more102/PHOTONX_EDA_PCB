# Stackup Inference

Stack-up inference is evidence based. Layer names observed in reconstructed
geometry establish ordering hints; dielectric materials and thicknesses are
unknown unless provided by source data.

## Gerber X2 copper ordering

PhotonX preserves Gerber X2 `.FileFunction` declarations from the
manufacturing manifest. For standard copper declarations such as
`Copper,L1,Top`, `Copper,L2,Inr`, and `Copper,L4,Bot`, the physical
ordinal is treated as source evidence rather than a filename heuristic.

When one unambiguous `Bot` declaration is present, its `L<p>` ordinal
declares the physical copper-layer count because Gerber X2 copper ordinals are
consecutive and the top layer is L1. PhotonX therefore includes declared but
geometry-empty inner copper layers in the stackup model. This prevents
downstream via-span and KiCad-export logic from treating a partial CAM package
as a smaller board.

For example, a package containing only:

- `Copper,L1,Top`
- `Copper,L4,Bot`

declares the copper order `F.Cu, In1.Cu, In2.Cu, B.Cu`, even if the L2/L3
Gerber files are absent from the supplied package.

Contradictory X2 declarations are fail-visible as
`X2_COPPER_STACKUP_CONFLICT`. PhotonX does not synthesize a declared stackup
from conflicting evidence; it falls back to layers actually observed in
reconstructed geometry.

This inference establishes copper count/order only. It does not infer
dielectric materials, dielectric thicknesses, copper weights, impedance
targets, or missing copper geometry.
