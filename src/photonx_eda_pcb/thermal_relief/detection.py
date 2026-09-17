from .model import ThermalRelief,ThermalSpoke

def infer_thermal(pad_id,zone_id,spoke_angles,width_mm=0.25,length_mm=0.6,gap_mm=0.2):
    spokes=[ThermalSpoke(float(a),float(width_mm),float(length_mm)) for a in spoke_angles]
    return ThermalRelief(pad_id,zone_id,spokes,float(gap_mm),True)
