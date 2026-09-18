def group_skew(group,lengths):
    vals=[float(lengths[n]) for n in group.nets if n in lengths]
    return None if len(vals)<2 else round(max(vals)-min(vals),6)
def within_group_tolerance(group,lengths):
    s=group_skew(group,lengths)
    return None if s is None or group.tolerance_mm is None else s<=group.tolerance_mm
