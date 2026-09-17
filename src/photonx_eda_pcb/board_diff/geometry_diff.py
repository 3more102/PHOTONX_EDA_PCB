def coordinate_delta(a,b):return (round(float(b[0])-float(a[0]),9),round(float(b[1])-float(a[1]),9))

def moved(a,b,tolerance_mm=1e-6):
    dx,dy=coordinate_delta(a,b)
    return abs(dx)>tolerance_mm or abs(dy)>tolerance_mm
