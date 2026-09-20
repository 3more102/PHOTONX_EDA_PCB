# Evidence-bounded footprint and package hints

PhotonX may attach a `package_hint` to a reconstructed `ComponentHypothesis` when pad geometry supports one of the explicitly modeled package topologies.

## Evidence priority

1. Gerber X2 component reference and pin attributes establish source identity when they are fully trusted.
2. Pad topology is used only to add a package hint to that already established identity.
3. Geometry never replaces, merges, or upgrades conflicting X2 identity.
4. Unsupported, weak, or ambiguous geometry remains unresolved.

## Topology features

The matcher derives orientation-invariant features from pad centers:

- pad count
- drilled-pad fraction
- one-row versus two-row topology
- pads per row and row balance
- minimum pad pitch
- within-row pitch regularity
- overall span/aspect information

Both principal-axis directions are evaluated so a wide SOIC/DIP remains a two-row package even when row spacing is larger than the row length.

## Supported hints

The current signature library recognizes:

- `TWO_PIN_THT`
- `TWO_PAD_SMD`
- `DIP8_LIKE`
- `SOIC8_LIKE`
- `SINGLE_ROW_THT`
- `SINGLE_ROW_SMD`
- `DUAL_ROW_THT`
- `DUAL_ROW_SMD`

These are package-shape hints, not part-number identification.

## Fail-closed rules

A package hint is not emitted when:

- the best score is below the acceptance threshold,
- the score margin to the runner-up is too small,
- the pad pitch is outside the modeled range,
- drill evidence contradicts the signature,
- row count, row balance, or pitch regularity contradicts the signature.

The component identity may still remain certain when X2 proves its reference. In that case `reference` and confidence are preserved while `package_hint` stays `None`, with an explicit unresolved reason in evidence.

## Regression coverage

Focused tests cover rotated SOIC-8 and DIP-8 patterns, regular single-row headers, deliberate signature ambiguity, implausibly large pad pitch, X2 package-hint propagation, and X2 identity preservation when package geometry is unproven.
