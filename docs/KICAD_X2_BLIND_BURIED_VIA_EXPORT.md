# KiCad export of X2 blind and buried vias

PhotonX exports a partial-layer plated point drill as a KiCad via only when the source evidence is strong enough to determine the via type without guessing.

## Required evidence

The via must satisfy all existing proven-via requirements and additionally:

- the drill has a canonical `layer_span` with `span_proven=True`;
- that canonical span matches the proven `via_spans` metadata endpoints;
- `x2_span_kind` is explicitly `blind` or `buried`;
- `blind` touches exactly one outer copper surface (`F.Cu` or `B.Cu`);
- `buried` touches neither outer copper surface.

A full-stack via may continue to export as a normal through via. If explicit X2 evidence says `blind` or `buried` while the canonical span is full-stack, PhotonX fails closed and omits the via.

## KiCad mapping

KiCad's board s-expression supports via types `blind` and `micro`; the absence of a type means through-hole. KiCad does not use a separate `buried` token. Therefore both source-proven X2 blind and buried vias are serialized with the KiCad `blind` type, while the endpoint layers preserve whether the via reaches a surface or stays internal.

PhotonX does not infer or emit `micro` from Gerber/Excellon X2 Blind/Buried evidence.

Reference: https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/#_track_via
