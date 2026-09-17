def within_tolerance(actual,target,tolerance):return abs(float(actual)-float(target))<=float(tolerance)

def clamp_dimension(value,minimum=0.0):return max(float(minimum),float(value))
