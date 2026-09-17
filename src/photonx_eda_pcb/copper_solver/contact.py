def point_distance(a,b):
    from math import hypot
    return hypot(a[0]-b[0],a[1]-b[1])

def points_touch(a,b,tolerance=0.01):return point_distance(a,b)<=tolerance

def intervals_overlap(a0,a1,b0,b1,tolerance=0.0):
    lo1,hi1=sorted((a0,a1));lo2,hi2=sorted((b0,b1));return not (hi1+tolerance<lo2 or hi2+tolerance<lo1)
