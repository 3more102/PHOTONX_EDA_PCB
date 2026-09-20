# Excellon subset

The helper modules recognize unit statements, tool definitions/selections, hits, routing commands and a constrained G85 slot syntax. Unsupported routing variants must remain explicit.

## XNC safety validation

For the supported XNC-compatible subset, `M30` is terminal: non-comment data after it is invalid and fails closed. Tool definitions must be unique, tool selections must reference a tool already present in the tool table, and tool diameters must decode to finite positive values. Strict mode raises parser errors for these violations; permissive mode emits `INVALID_EXCELLON_*` diagnostics and suppresses geometry from the affected file.

## Tool identifier grammar

Tool identifiers use ASCII decimal digits only. Unicode digit lookalikes and malformed `T...` selections/definitions are rejected. Permissive parsing suppresses file geometry and reports an `INVALID_EXCELLON_TOOL_*` diagnostic rather than accepting a visually similar identifier.


## X2-compatible plating evidence

PhotonX recognizes the bounded KiCad-style X2-compatible structured comments used in Excellon drill files:

- `; #@! TF.FileFunction,Plated|NonPlated|MixedPlating,<start-layer>,<end-layer>,PTH|NPTH|Blind|Buried[,Drill|Rout|Mixed]`
- `; #@! TA.AperFunction,Plated|NonPlated,PTH|NPTH|Blind|Buried,ViaDrill|ComponentDrill`
- `; #@! TD` to clear the modal aperture-function evidence.

The file-level copper-layer ordinals are preserved on point drills, G85 slots, and routed paths as normalized raw evidence in `x2_layer_span` plus `x2_span_kind`. Layer numbers are one-based and a span must reference two distinct copper layers. Reversed from/to order is normalized because the Gerber FileFunction definition treats that order as insignificant. The canonical `layer_span` and `span_proven` fields are populated only after those ordinals are safely mapped onto the reconstructed copper stack.

A specific file-level `Plated` or `NonPlated` claim applies when a tool has no stronger tool-level claim. `MixedPlating` deliberately resolves to `unknown` unless a tool-level `TA.AperFunction` proves the tool's plating. Conflicting specific file/tool claims, conflicting file claims, and malformed recognized plating attributes fail closed; permissive mode emits `INVALID_EXCELLON_X2_PLATING` and suppresses file geometry.

The resolved plating state is carried into drill hits, G85 slots, and routed paths with provenance evidence. Unrelated structured comments remain metadata-only and do not create plating claims.


## X2 layer-span resolution

Explicit drill, slot, and routed-path spans are not converted directly into KiCad layer names unless the copper stack order is itself ordinal-addressable. The preferred mapping source is a conflict-free Gerber X2 copper stackup with a declared bottom-layer ordinal. For legacy two-layer packages, `PTH/NPTH L1..L2` may map to `F.Cu..B.Cu` when those are the only reconstructed copper layers.

Blind or buried spans never use the two-layer shortcut. If an explicit point-drill span exceeds the declared stackup or cannot be mapped safely, PhotonX suppresses vertical connectivity and emits `X2_DRILL_SPAN_UNRESOLVED`; it does not fall back to a wider geometry-derived via span. G85 slots and routed paths use the same ordinal mapper and retain `layer_span=None`/`span_proven=False` with `X2_SLOT_SPAN_UNRESOLVED` or `X2_ROUTE_SPAN_UNRESOLVED` when their explicit X2 spans cannot be mapped. When an exact plated point-drill span later reaches KiCad export, partial-layer export additionally requires `span_proven=True`, an exact canonical `layer_span`, and explicit X2 `Blind` or `Buried` kind evidence consistent with the endpoints. PhotonX keeps blind/buried semantics internally, but its current KiCad `20240108` target serializes both using KiCad's legacy `blind` token; inner-to-inner `blind` readback is normalized back to semantic `buried`. Untyped/PTH partial spans and kind/topology contradictions remain explicit omissions.
