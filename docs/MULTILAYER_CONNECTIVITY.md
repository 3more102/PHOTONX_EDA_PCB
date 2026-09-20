# Multilayer Connectivity

PHOTONX keeps XY overlap and vertical electrical connectivity as separate claims.

The reconstruction pipeline now resolves via-span candidates after drill-to-pad association and stack-up inference. A cross-layer PhysicalGraph edge is created only when all of the following are true:

- the drill has explicit `plated` evidence;
- the via span is proven from copper-pad observations on at least two copper layers;
- the connected pad IDs are the exact candidates retained by the span resolver.

A proven span therefore produces `plated_via_span` graph edges between overlapping pad candidates on different layers. The edge records the drill ID, inferred span endpoints, confidence, and evidence strings. Physical-net provenance carries that same evidence, and the net confidence is bounded by the weakest via-span confidence used by the connected component.

Unknown plating never creates a vertical electrical bridge. When a drill overlaps copper on multiple layers but its plating remains unknown, the normal reconstruction path emits `MULTILAYER_SPAN_UNKNOWN` and leaves the layers electrically separate. Explicit non-plated holes also remain separate, without being mislabeled as unknown.

Same-layer copper contact still uses the existing geometry predicates. Cross-layer connectivity is never inferred from XY coincidence alone.

Current scope is intentionally conservative: the vertical bridge is established through observed pad candidates used to prove the via span. Region-only or track-only barrel contact without pad evidence remains unresolved rather than guessed.
