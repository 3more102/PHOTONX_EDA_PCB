from .model import SlotConnectivityCandidate
from photonx_eda_pcb.plated_slot_inference.contacts import slot_pad_contacts
def _layer_key(layer):
    if layer=="F.Cu":return (0,layer)
    if layer=="B.Cu":return (999,layer)
    return (500,layer)
def resolve_slot_connectivity(board,slot,tolerance_mm=.03):
    pads=slot_pad_contacts(board,slot,tolerance_mm);layers=tuple(sorted({p.layer for p in pads},key=_layer_key));nets=tuple(sorted({p.net_id for p in pads if p.net_id is not None}))
    proven=str(slot.plated).lower().replace("_","-")=="plated" and len(layers)>=2
    conflict=len(nets)>1
    confidence=.95 if proven and not conflict else (.6 if proven else .25)
    ev=["slot_pad_geometry"]+(["slot_plating_proven"] if proven else [])+(["net_conflict"] if conflict else [])
    return SlotConnectivityCandidate(slot.id,layers,tuple(sorted(p.id for p in pads)),nets,proven,conflict,confidence,tuple(ev))
