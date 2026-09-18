from .model import ViaTransition
def analyze_transition(id,net_id,start_layer,end_layer,drill_mm,pad_mm,nearby_return_vias=0,stub_layers=0):
    ev=["drill_geometry"]
    if start_layer and end_layer:ev.append("layer_span")
    if nearby_return_vias:ev.append("return_vias")
    conf=.45+(.3 if start_layer and end_layer else 0)+(.25 if nearby_return_vias else 0)
    return ViaTransition(str(id),None if net_id is None else str(net_id),str(start_layer),str(end_layer),float(drill_mm),float(pad_mm),int(nearby_return_vias),int(stub_layers),round(min(conf,1),6),ev)
