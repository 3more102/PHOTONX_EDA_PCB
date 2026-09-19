from __future__ import annotations

# Excellon machine-program numeric fields are ASCII-defined. Keep identifiers
# and coordinate tokens separate so Unicode digit lookalikes never enter the
# production parser through Python's Unicode-aware \\d regex class.
TOOL_NUMBER_PATTERN = r"[0-9]+"

# Excellon coordinates may be integer-format tokens or explicit decimal values.
# Keep the lexical grammar strict enough that malformed tokens such as ".", "1..2",
# and sign-only values never reach float()/CoordinateFormat decoding.
UNSIGNED_DECIMAL_PATTERN = r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)"
SIGNED_DECIMAL_PATTERN = rf"[+-]?{UNSIGNED_DECIMAL_PATTERN}"
