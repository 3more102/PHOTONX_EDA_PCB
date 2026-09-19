# Multilayer Connectivity

Layer-qualified nodes and explicit via-span edges model vertical electrical connectivity. Cross-layer connections require plating/span evidence and must not be inferred from XY overlap alone.

## Via-span evidence boundary

`resolve_via_spans()` distinguishes an observed geometric hypothesis from a proven electrical span:

- pad candidates overlapping one drill on multiple copper layers establish candidate endpoints only;
- `plating == "plated"` by itself does not prove which copper layers the barrel spans;
- an authoritative span may be supplied on the drill as `layer_span=(start_layer, end_layer)`;
- a span is marked proven only when `span_proven` is true, the drill is explicitly plated, both endpoints exist in the ordered stackup, and observed pad evidence does not contradict that interval;
- malformed or out-of-stackup explicit span metadata fails closed instead of falling back to a weaker XY-overlap guess;
- an observed copper layer outside an explicit span is retained as a conflict and prevents the candidate from being marked proven.

This keeps blind/buried/through-hole uncertainty visible while still preserving a useful candidate span for review.
