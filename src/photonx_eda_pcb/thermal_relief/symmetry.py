from .geometry import angular_gaps

def symmetry_error(spokes):
    gaps=angular_gaps(spokes)
    if not gaps:return 360.0
    avg=sum(gaps)/len(gaps)
    return max(abs(g-avg) for g in gaps)

def is_symmetric(spokes,tolerance_deg=5.0):return symmetry_error(spokes)<=tolerance_deg
