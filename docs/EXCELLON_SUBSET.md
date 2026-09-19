# Excellon subset

The helper modules recognize unit statements, tool definitions/selections, hits, routing commands and a constrained G85 slot syntax. Unsupported routing variants must remain explicit.

Tool identifiers use ASCII decimal digits only. Unicode digit lookalikes and malformed `T...` selections/definitions are rejected; permissive parsing suppresses file geometry and reports an `INVALID_EXCELLON_TOOL_*` diagnostic rather than accepting a visually similar identifier.
