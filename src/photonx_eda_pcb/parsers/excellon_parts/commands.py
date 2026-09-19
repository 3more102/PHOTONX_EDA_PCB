import re

from ...excellon_numeric import SIGNED_DECIMAL_PATTERN
from .slots import is_canned_slot

_PROGRAM_END = re.compile(
    rf"^M(?:00|30)(?:X{SIGNED_DECIMAL_PATTERN})?(?:Y{SIGNED_DECIMAL_PATTERN})?$"
)


def is_program_end(text: str) -> bool:
    return _PROGRAM_END.fullmatch(text.strip().upper()) is not None


def classify_excellon_command(text: str) -> str:
    s = text.strip().upper()
    if s == "M48":
        return "header_begin"
    if s in {"M95", "%"}:
        return "header_end"
    if s.startswith(("METRIC", "INCH")) or s in {"M71", "M72"}:
        return "units"
    if s.startswith("T"):
        return "tool"
    if "G85" in s and is_canned_slot(s):
        return "slot"
    if s.startswith(("G00", "G01", "G02", "G03")):
        return "route"
    if is_program_end(s):
        return "eof"
    if ("X" in s or "Y" in s) and not s.startswith("G") and "G85" not in s:
        return "hit"
    return "unknown"
