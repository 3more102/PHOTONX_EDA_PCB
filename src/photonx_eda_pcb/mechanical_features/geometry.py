from shapely.geometry import LineString,Point
def slot_shape(slot):
    return LineString([slot.start,slot.end]).buffer(float(slot.width_mm)/2,cap_style=1)
def hole_shape(hole):
    return Point(*hole.center).buffer(float(hole.diameter_mm)/2)
