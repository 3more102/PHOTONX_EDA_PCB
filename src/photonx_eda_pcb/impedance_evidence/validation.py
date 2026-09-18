def validate_impedance(value):
    if value is None:return []
    return [] if 1<=float(value)<=1000 else ["IMPEDANCE_OUT_OF_RANGE"]
