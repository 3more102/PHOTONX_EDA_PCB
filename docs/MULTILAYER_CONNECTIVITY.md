# Multilayer Connectivity

PHOTONX keeps XY overlap and vertical electrical connectivity as separate claims.

The reconstruction pipeline resolves via-span candidates after drill-to-pad association and stack-up inference. A cross-layer PhysicalGraph edge is created only when the via span is proven and the matching source drill still carries explicit `plated` evidence.

A resolved span retains its complete traversed copper-layer path in `ViaSpanCandidate.layer_ids`. The normal reconstruction metadata serializes that path so downstream audits can see exactly which copper layers were considered inside the proven span.

When an Excellon X2-compatible `TF.FileFunction` explicitly declares drill ordinals, that source span takes precedence over geometry-derived outermost overlap. PhotonX maps the ordinals only against a declared X2 copper stack order, except for the bounded two-layer `PTH/NPTH L1..L2` case. Blind and buried spans without a trustworthy ordinal stack remain unresolved and cannot silently widen to `F.Cu..B.Cu`.

The pad candidates that prove a span remain connected as `pad_span` contacts. Tracks, pads, and `CopperRegion` objects on layers inside that span may additionally participate as `barrel_touch` contacts, but only when reconstructed copper reaches the finished drill wall within the configured connectivity tolerance.

The barrel-contact predicate uses the drill boundary, not the complete drilled-hole disk. Copper that lies entirely inside the removed hole volume without reaching the wall therefore remains electrically separate. XY coincidence with the drill center is not sufficient evidence.

Unknown and explicitly non-plated drills never create vertical electrical bridges. A caller-supplied `proven=True` span cannot override the plating state stored on the source `DrillHit`.

Physical-net provenance distinguishes the pad IDs that proved the span from additional barrel-contact object IDs. Net confidence remains bounded by the weakest participating plated-via span confidence.

Same-layer copper contact continues to use the normal geometry predicates. Cross-layer connectivity is never inferred from XY overlap alone.
