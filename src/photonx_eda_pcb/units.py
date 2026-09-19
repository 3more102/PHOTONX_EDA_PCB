from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


def _validate_coordinate_token(raw: str) -> tuple[float, str]:
    if not isinstance(raw, str):
        raise ValueError("coordinate must be a string")
    if not raw:
        raise ValueError("coordinate must not be empty")

    sign = -1.0 if raw.startswith("-") else 1.0
    digits = raw[1:] if raw.startswith(("-", "+")) else raw
    if not digits or digits == ".":
        raise ValueError(f"invalid coordinate {raw!r}")
    if digits.count(".") > 1:
        raise ValueError(f"invalid coordinate {raw!r}")
    if any(ch != "." and not ("0" <= ch <= "9") for ch in digits):
        raise ValueError(f"invalid coordinate {raw!r}")
    return sign, digits


@dataclass(frozen=True)
class CoordinateFormat:
    integer: int
    decimal: int
    zero_suppression: str = "L"

    def __post_init__(self) -> None:
        if (
            isinstance(self.integer, bool)
            or not isinstance(self.integer, int)
            or self.integer < 0
        ):
            raise ValueError("integer digits must be a non-negative integer")
        if (
            isinstance(self.decimal, bool)
            or not isinstance(self.decimal, int)
            or self.decimal < 0
        ):
            raise ValueError("decimal digits must be a non-negative integer")
        if self.integer + self.decimal <= 0:
            raise ValueError("coordinate format must contain at least one digit")
        if self.zero_suppression not in {"L", "T"}:
            raise ValueError(
                f"unsupported zero suppression {self.zero_suppression!r}"
            )

    def decode(self, raw: str) -> float:
        sign, digits = _validate_coordinate_token(raw)
        if "." in digits:
            value = sign * float(digits)
            if not isfinite(value):
                raise ValueError(f"coordinate {raw!r} must be finite")
            return value

        total = self.integer + self.decimal
        if len(digits) > total:
            raise ValueError(
                f"coordinate {raw!r} exceeds format {self.integer}.{self.decimal}"
            )
        if self.zero_suppression == "L":
            digits = digits.rjust(total, "0")
        else:
            digits = digits.ljust(total, "0")
        return sign * int(digits) / (10 ** self.decimal)


def to_mm(value: float, units: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError("value must be a finite number")
    if units == "mm":
        converted = value
    elif units == "inch":
        converted = value * 25.4
    else:
        raise ValueError(f"unsupported units {units!r}")
    if not isfinite(converted):
        raise ValueError("converted millimeter value must be finite")
    return converted
