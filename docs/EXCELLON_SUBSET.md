# Excellon subset

The helper modules recognize unit statements, tool definitions/selections, hits, routing commands and a constrained G85 slot syntax. Unsupported routing variants must remain explicit.

## XNC end-of-file handling

Ucamco XNC `M30` is treated as the formal end-of-file command. Blank lines may follow it, but any later non-blank command is invalid: strict parsing rejects the file, while permissive parsing records `INVALID_EXCELLON_DATA_AFTER_M30` and suppresses the file's reconstructed geometry so post-terminator data cannot leak into manufacturing evidence.

