import re

from ...excellon_numeric import SIGNED_DECIMAL_PATTERN

_COORD = SIGNED_DECIMAL_PATTERN
_CANON = re.compile(
    rf"^X(?P<x1>{_COORD})Y(?P<y1>{_COORD})G85X(?P<x2>{_COORD})Y(?P<y2>{_COORD})$"
)
_LEGACY = re.compile(
    rf"^G85X(?P<x1>{_COORD})Y(?P<y1>{_COORD})X(?P<x2>{_COORD})Y(?P<y2>{_COORD})$"
)


def parse_slot_command(text: str) -> tuple[str, str, str, str]:
    s = text.strip().upper()
    m = _CANON.fullmatch(s) or _LEGACY.fullmatch(s)
    if not m:
        raise ValueError("unsupported slot command")
    return m["x1"], m["y1"], m["x2"], m["y2"]


def is_canned_slot(text: str) -> bool:
    try:
        parse_slot_command(text)
        return True
    except ValueError:
        return False
