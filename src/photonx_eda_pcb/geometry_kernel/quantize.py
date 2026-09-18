from decimal import Decimal,ROUND_HALF_EVEN
def quantize_value(value,step=1e-6):
    q=Decimal(str(step))
    if q<=0:raise ValueError("step must be positive")
    return float((Decimal(str(value))/q).quantize(Decimal("1"),rounding=ROUND_HALF_EVEN)*q)
def quantize_point(x,y,step=1e-6):return (quantize_value(x,step),quantize_value(y,step))
