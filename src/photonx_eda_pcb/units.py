from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class CoordinateFormat:
    integer: int
    decimal: int
    zero_suppression: str = "L"

    def decode(self, raw: str) -> float:
        sign = -1.0 if raw.startswith("-") else 1.0
        digits = raw[1:] if raw.startswith(("-", "+")) else raw
        if "." in digits:
            return sign * float(digits)
        total = self.integer + self.decimal
        if len(digits) > total:
            raise ValueError(f"coordinate {raw!r} exceeds format {self.integer}.{self.decimal}")
        if self.zero_suppression == "L":
            digits = digits.rjust(total, "0")
        elif self.zero_suppression == "T":
            digits = digits.ljust(total, "0")
        else:
            raise ValueError(f"unsupported zero suppression {self.zero_suppression!r}")
        return sign * int(digits) / (10 ** self.decimal)


def to_mm(value: float, units: str) -> float:
    if units == "mm":
        return value
    if units == "inch":
        return value * 25.4
    raise ValueError(f"unsupported units {units!r}")
