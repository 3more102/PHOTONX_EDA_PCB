# Excellon subset

The helper modules recognize unit statements, tool definitions/selections, hits, routing commands and a constrained G85 slot syntax. Unsupported routing variants must remain explicit. Any unrecognized Excellon statement is fail-closed: strict parsing rejects it, while permissive parsing records `UNKNOWN_EXCELLON_STATEMENT` and suppresses all geometry from that file.
