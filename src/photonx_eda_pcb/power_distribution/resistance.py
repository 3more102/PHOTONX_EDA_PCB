COPPER_RESISTIVITY_OHM_M=1.724e-8
def copper_resistance(length_mm,width_mm,thickness_um=35.0,resistivity=COPPER_RESISTIVITY_OHM_M):
    l=float(length_mm)*1e-3;w=float(width_mm)*1e-3;t=float(thickness_um)*1e-6
    if min(l,w,t)<=0:raise ValueError("positive conductor dimensions required")
    return float(resistivity)*l/(w*t)
