from math import log
def microstrip_estimate(width_mm,height_mm,er,thickness_mm=0.035):
    w=float(width_mm)+float(thickness_mm)
    h=float(height_mm); e=float(er)
    if w<=0 or h<=0 or e<=1:raise ValueError("invalid microstrip parameters")
    wh=w/h
    ee=(e+1)/2+(e-1)/2*(1/(1+12/wh))**0.5
    if wh<=1:return 60/(ee**0.5)*log(8/wh+0.25*wh)
    return 120*3.141592653589793/(ee**0.5*(wh+1.393+0.667*log(wh+1.444)))
