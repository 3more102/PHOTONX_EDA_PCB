def polarity_conflict(a,b):
    return bool((a.positive_pin and b.negative_pin and a.positive_pin==b.negative_pin) or (a.negative_pin and b.positive_pin and a.negative_pin==b.positive_pin))
def orientation_delta(a,b):
    return abs((a.rotation_deg-b.rotation_deg+180)%360-180)
