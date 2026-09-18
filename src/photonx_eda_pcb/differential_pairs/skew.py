from .geometry import polyline_length
def pair_skew(path_a,path_b):
    return abs(polyline_length(path_a)-polyline_length(path_b))
