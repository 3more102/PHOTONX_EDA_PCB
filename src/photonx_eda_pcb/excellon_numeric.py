from __future__ import annotations

# Excellon machine-program identifiers are ASCII-defined.\nTOOL_NUMBER_PATTERN = r"[0-9]+"\n\n# Excellon coordinates may be integer-format tokens or explicit decimal values.
# Keep the lexical grammar strict enough that malformed tokens such as ".", "1..2",
# and sign-only values never reach float()/CoordinateFormat decoding.
UNSIGNED_DECIMAL_PATTERN = r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)"
SIGNED_DECIMAL_PATTERN = rf"[+-]?{UNSIGNED_DECIMAL_PATTERN}"
