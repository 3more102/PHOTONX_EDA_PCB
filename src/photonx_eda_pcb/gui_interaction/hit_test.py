from math import hypot
def nearest_point(point,candidates,max_distance):
    best=None
    for object_id,p in candidates:
        d=hypot(float(point[0])-float(p[0]),float(point[1])-float(p[1]))
        if d<=max_distance and (best is None or d<best[1]):best=(object_id,d)
    return best
