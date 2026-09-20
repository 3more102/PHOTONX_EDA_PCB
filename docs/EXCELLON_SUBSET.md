# Excellon subset

The helper modules recognize unit statements, tool definitions/selections, hits, routing commands and a constrained G85 slot syntax. Unsupported routing variants must remain explicit.

## XNC safety validation

For the supported XNC-compatible subset, `M30` is terminal: non-comment data after it is invalid and fails closed. Tool definitions must be unique, tool selections must reference a tool already present in the tool table, and tool diameters must decode to finite positive values. Strict mode raises parser errors for these violations; permissive mode emits `INVALID_EXCELLON_*` diagnostics and suppresses geometry from the affected file.

## Tool identifier grammar

Tool identifiers use ASCII decimal digits only. Unicode digit lookalikes and malformed `T...` selections/definitions are rejected. Permissive parsing suppresses file geometry and reports an `INVALID_EXCELLON_TOOL_*` diagnostic rather than accepting a visually similar identifier.


## X2-compatible plating evidence

PhotonX recognizes the bounded KiCad-style X2-compatible structured comments used in Excellon drill files:

- `; #@! TF.FileFunction,Plated|NonPlated|MixedPlating,<start-layer>,<end-layer>,PTH|NPTH|Blind|Buried[,Drill|Route|Mixed]`
- `; #@! TA.AperFunction,Plated|NonPlated,PTH|NPTH|Blind|Buried,ViaDrill|ComponentDrill`
- `; #@! TD` to clear the modal aperture-function evidence.

A specific file-level `Plated` or `NonPlated` claim applies when a tool has no stronger tool-level claim. `MixedPlating` deliberately resolves to `unknown` unless a tool-level `TA.AperFunction` proves the tool's plating. Conflicting specific file/tool claims, conflicting file claims, and malformed recognized plating attributes fail closed; permissive mode emits `INVALID_EXCELLON_X2_PLATING` and suppresses file geometry.

The resolved plating state is carried into drill hits, G85 slots, and routed paths with provenance evidence. Unrelated structured comments remain metadata-only and do not create plating claims.
