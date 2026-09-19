from math import isfinite
import re

_UNSIGNED_DECIMAL_PATTERN = r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)"
_RE = re.compile(
    rf"%SR(?:X(?P<x>[0-9]+))?(?:Y(?P<y>[0-9]+))?"
    rf"(?:I(?P<i>{_UNSIGNED_DECIMAL_PATTERN}))?"
    rf"(?:J(?P<j>{_UNSIGNED_DECIMAL_PATTERN}))?\*%"
)


def parse_step_repeat(text: str) -> dict[str, float | int]:
    m = _RE.fullmatch(text.strip())
    if not m:
        raise ValueError("invalid step-repeat")
    if not any(m.groupdict().values()):
        return {"x": 1, "y": 1, "i": 0.0, "j": 0.0}

    x_count = int(m["x"] or 1)
    y_count = int(m["y"] or 1)
    x_step = float(m["i"] or 0)
    y_step = float(m["j"] or 0)
    if not isfinite(x_step) or not isfinite(y_step):
        raise ValueError("non-finite step-repeat offset")
    return {"x": x_count, "y": y_count, "i": x_step, "j": y_step}
