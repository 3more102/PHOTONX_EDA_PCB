from math import pi,sqrt
def rc_cutoff_hz(resistance_ohm,capacitance_f):
    r=float(resistance_ohm);c=float(capacitance_f)
    if r<=0 or c<=0:return None
    return 1/(2*pi*r*c)
def lc_resonance_hz(inductance_h,capacitance_f):
    l=float(inductance_h);c=float(capacitance_f)
    if l<=0 or c<=0:return None
    return 1/(2*pi*sqrt(l*c))
