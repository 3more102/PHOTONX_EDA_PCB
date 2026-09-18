def current_density_a_per_mm2(current_a,width_mm,thickness_um=35.0):
    area=float(width_mm)*(float(thickness_um)*1e-3)
    if area<=0:raise ValueError("positive cross-section required")
    return float(current_a)/area
