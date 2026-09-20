# Gerber X2 footprint boundaries

PhotonX footprint inference now treats fully trusted Gerber X2 component-reference
evidence as a source-proven **component boundary** before geometric pad
clustering.

## Evidence boundary

Only `gerber_x2_component_refdes` evidence with confidence `1.0` is promoted.
Pads with one trusted reference are grouped by reference plus trusted
step-repeat instance evidence. This allows a source-proven component to span a
distance larger than the geometric clustering threshold without being split.

The source-proven boundary does **not** prove the package type. Signature
matching remains heuristic and keeps its own `confidence` score. The
`FootprintCandidate` therefore exposes separate fields:

- `reference`: trusted source reference when available;
- `boundary_source`: `gerber_x2_component_refdes`,
  `gerber_x2_refdes_conflict`, or `geometric_proximity`;
- `boundary_confidence`: `1.0` only for an unambiguous trusted X2 boundary,
  otherwise `0.0`;
- `confidence`: package/signature match confidence, unchanged in meaning.

Trusted X2 pin-number and pin-function evidence is preserved in the candidate
evidence for review.

## Fail-closed behavior

A pad carrying multiple trusted X2 component references, or an empty trusted
reference, is isolated as a conflict candidate with zero confidence. It is
withheld from geometric clustering so proximity cannot silently overwrite
contradictory source identity.

Lower-confidence X2 reference evidence is not promoted. Those pads remain
eligible for the existing geometric footprint hypothesis path.

## Determinism

Footprint candidate IDs are derived from stable source identity and sorted pad
IDs rather than enumeration order. Reordering input pads therefore does not
change the candidate identity.
