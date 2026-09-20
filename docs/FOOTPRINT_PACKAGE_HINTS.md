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


## Structured source pin identity

When trusted Gerber X2 `.P` evidence proves a component reference and a pad has exactly one trusted non-empty pin number, the corresponding `ComponentHypothesis` stores that relationship in `source_pin_map` as `pad_id -> source pin number`.

Trusted pin functions are stored separately in `source_pin_functions`, but only for pads that also have a proven source pin number. Conflicting, empty, missing, or lower-confidence pin evidence is not promoted into these maps and remains explicitly unresolved in the human-readable evidence.

The structured pin maps and `package_hint` coexist on the same component object but have different authority:

- `source_pin_map` / `source_pin_functions` preserve source-declared identity only.
- `package_hint` remains a geometry-backed package-shape hypothesis.
- Geometry never invents or renumbers source pins.
- Conflicting trusted pin numbers fail closed for that pad without discarding an otherwise proven component reference.


### KiCad grouping authority

When PhotonX groups a source-proven X2 component into `PHOTONX:RecoveredX2Component`, the exporter consumes `ComponentHypothesis.source_pin_map` and `source_pin_functions` as the canonical machine-readable pin identity produced by reconstruction. It does not independently re-derive pin numbers from pad provenance during export.

Grouping remains fail-closed: the pin map must be a dictionary, cover every component pad exactly once by membership, contain non-empty string pin numbers, keep function entries bound to mapped pads, use unique pin numbers within the component, and retain matching trusted X2 refdes evidence on every grouped pad. Any violation falls back to independent recovered pads with an explicit `KICAD_X2_COMPONENT_IDENTITY_NOT_GROUPED` issue.
