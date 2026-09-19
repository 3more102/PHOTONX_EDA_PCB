import re

from ...excellon_numeric import SIGNED_DECIMAL_PATTERN

_RE = re.compile(
    rf"(?:X(?P<x>{SIGNED_DECIMAL_PATTERN}))?(?:Y(?P<y>{SIGNED_DECIMAL_PATTERN}))?"
)


def parse_excellon_xy(text: str) -> dict[str, str | None]:
    m = _RE.fullmatch(text.strip())
    if not m or (m["x"] is None and m["y"] is None):
        raise ValueError("invalid Excellon coordinate")
    return m.groupdict()
