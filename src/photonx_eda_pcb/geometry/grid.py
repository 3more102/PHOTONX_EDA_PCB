from decimal import Decimal, ROUND_HALF_EVEN
from ..models import Point

def quantize(value: float, step: float) -> float:
    if step <= 0:
        raise ValueError("step must be positive")
    dstep = Decimal(str(step))
    q = (Decimal(str(value)) / dstep).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN)
    return float(q * dstep)

def quantize_point(p: Point, step: float) -> Point:
    return Point(quantize(p.x, step), quantize(p.y, step))
