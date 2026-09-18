def within_distance(a,b,distance_mm,tolerance_mm=0.0):
    return a.distance(b)<=float(distance_mm)+float(tolerance_mm)
def covers_with_tolerance(container,shape,tolerance_mm=0.0):
    return container.buffer(float(tolerance_mm)).covers(shape)
