# Footprint Spatial Clustering

Pad clustering uses radius-neighbor queries and deterministic breadth-first connected components rather than repeatedly scanning every remaining pad.

The default behavior intentionally preserves the existing single-linkage proximity semantics: if pad A is near B and B is near C, all three can belong to one connected pad group even when A and C are farther apart than the proximity threshold.

## Optional anti-bridging span guard

Callers that need a more conservative grouping can set `max_cluster_span_mm` on `cluster_pads()`, `cluster_pads_bruteforce()`, or `infer_footprints()`.

When enabled, each proximity-connected group is first deterministically partitioned so every pad in a guarded bucket stays within the configured center-to-center span of every other pad in that bucket. Each guarded bucket is then re-partitioned into connected components under the original `max_gap_mm` rule. The result therefore cannot contain pads that are only grouped by the span rule after their max-gap bridge was assigned elsewhere.

The guard is opt-in and does not change existing default results. It is a clustering policy, not evidence that the resulting group is a true component footprint; nearby unrelated pads can still require silkscreen, BOM, placement, package, or human-review evidence.

The spatial and brute-force implementations are regression-tested for identical guarded grouping semantics.
