def default_assumptions(er=None,height_mm=None):
    a=[]
    if er is None:a.append("dielectric_constant_unknown")
    if height_mm is None:a.append("reference_plane_distance_unknown")
    return tuple(a)
