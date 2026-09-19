from math import isfinite
import re


_UNSIGNED_DECIMAL_PATTERN = r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)"
_RE = re.compile(
    rf"%SR"
    rf"(?:X(?P<x>\d+))?"
    rf"(?:Y(?P<y>\d+))?"
    rf"(?:I(?P<i>{_UNSIGNED_DECIMAL_PATTERN}))?"
    rf"(?:J(?P<j>{_UNSIGNED_DECIMAL_PATTERN}))?"
    rf"\*%"
)


def parse_step_repeat(text: str) -> dict[str, float | int]:
    match = _RE.fullmatch(text.strip())
    if not match:
        raise ValueError("invalid step-repeat")
    if not any(match.groupdict().values()):
        return {"x": 1, "y": 1, "i": 0.0, "j": 0.0}

    x_count = int(match["x"] or 1)
    y_count = int(match["y"] or 1)
    x_step = float(match["i"] or 0)
    y_step = float(match["j"] or 0)
    if not isfinite(x_step) or not isfinite(y_step):
        raise ValueError("step-repeat increments must be finite")

    return {"x": x_count, "y": y_count, "i": x_step, "j": y_step}
