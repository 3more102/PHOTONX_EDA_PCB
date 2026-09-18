from math import hypot
def route_length_mm(route):
    return round(sum(hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(route.points,route.points[1:])),6)
def route_segment_count(route):return max(0,len(route.points)-1)
