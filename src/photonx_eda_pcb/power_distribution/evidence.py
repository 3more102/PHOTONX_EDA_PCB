def pdn_confidence(has_power_label=False,has_stackup=False,has_current=False,has_plane=False):
    score=(.3 if has_power_label else 0)+(.2 if has_stackup else 0)+(.3 if has_current else 0)+(.2 if has_plane else 0)
    return round(min(score,1.0),12)
