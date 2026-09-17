def semantic_confidence(kind,nearby_copper=False,nearby_component=False):
    base={'net_label_candidate':0.45,'reference_resistor':0.65,'reference_capacitor':0.65,'reference_ic':0.7,'reference_diode':0.65,'reference_connector':0.65}.get(kind,0.1)
    if nearby_copper:base+=0.1
    if nearby_component:base+=0.15
    return round(min(base,1.0),12)
