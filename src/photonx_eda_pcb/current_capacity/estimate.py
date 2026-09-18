from .model import CurrentCapacityEstimate
from .cross_section import cross_section_mm2
def estimate_current_capacity(net_id,width_mm,copper_um=35,temp_rise_c=10,external=True,confidence=.5):
    area=cross_section_mm2(width_mm,copper_um)
    if area<=0 or temp_rise_c<=0:raise ValueError("positive geometry and temperature rise required")
    k=.048 if external else .024
    current=k*(float(temp_rise_c)**.44)*((area*1550.0031)**.725)
    assumptions=["empirical_trace_capacity","external_layer" if external else "internal_layer"]
    return CurrentCapacityEstimate(str(net_id),float(width_mm),float(copper_um),float(temp_rise_c),round(current,6),round(min(1,max(0,float(confidence))),6),assumptions)
