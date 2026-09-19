# Excellon subset

The helper modules recognize unit statements, tool definitions/selections, hits, routing commands and a constrained G85 slot syntax. Unsupported routing variants must remain explicit.

## XNC safety validation

For the supported XNC-compatible subset, `M30` is terminal: non-comment data after it is invalid and fails closed. Tool definitions must be unique, tool selections must reference a tool already present in the tool table, and tool diameters must decode to finite positive values. Strict mode raises parser errors for these violations; permissive mode emits `INVALID_EXCELLON_*` diagnostics and suppresses geometry from the affected file.
