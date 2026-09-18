from shapely.geometry import LineString,Point
def route_shape(route):
    if len(route.points)>=2:
        return LineString(route.points).buffer(float(route.width_mm)/2,cap_style=1,join_style=1)
    if len(route.points)==1:
        return Point(*route.points[0]).buffer(float(route.width_mm)/2)
    return Point(0,0).buffer(0)
