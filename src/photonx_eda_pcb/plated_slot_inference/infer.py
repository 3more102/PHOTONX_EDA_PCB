from math import hypot
from .model import PlatedSlotPadstack,PadstackInference
from .contacts import slot_pad_contacts
from photonx_eda_pcb.mechanical_features.measure import slot_geometry_descriptor
from photonx_eda_pcb.geometry_kernel import pad_shape
from photonx_eda_pcb.mechanical_features.geometry import slot_shape

def _near(a,b,tol):return abs(float(a)-float(b))<=float(tol)
def _orthogonal(angle,tol_deg=1e-3):
    a=float(angle)%180
    if min(abs(a),abs(a-90),abs(a-180))<=tol_deg:return 0 if abs(a)<tol_deg or abs(a-180)<tol_deg else 90
    return None
def _layer_key(layer):
    if layer=="F.Cu":return (0,layer)
    if layer=="B.Cu":return (999,layer)
    if layer.startswith("In") and layer.endswith(".Cu"):
        try:return (int(layer[2:-3]),layer)
        except ValueError:pass
    return (500,layer)

def infer_plated_slot_padstack(board,slot,tolerance_mm=.03):
    if str(slot.plated).lower().replace("_","-")!="plated":return PadstackInference(slot.id,None,("SLOT_NOT_PROVEN_PLATED",))
    desc=slot_geometry_descriptor(slot);orth=_orthogonal(desc["angle_deg"])
    if orth is None:return PadstackInference(slot.id,None,("SLOT_ANGLE_NON_ORTHOGONAL",))
    contacts=slot_pad_contacts(board,slot,tolerance_mm)
    covering=[p for p in contacts if pad_shape(p).buffer(tolerance_mm).covers(slot_shape(slot))]
    if not covering:return PadstackInference(slot.id,None,("SLOT_NO_COPPER_PAD_COVERAGE",))
    by_layer={}
    for p in covering:
        by_layer.setdefault(p.layer,[]).append(p)
    selected=[]
    for layer,items in by_layer.items():
        items=sorted(items,key=lambda p:(pad_shape(p).area,p.id));selected.append(items[0])
    if len(selected)<2:return PadstackInference(slot.id,None,("SLOT_PADSTACK_NEEDS_MULTILAYER_EVIDENCE",))
    centers=[(p.center.x,p.center.y) for p in selected];cx,cy=desc["center"]
    if any(hypot(x-cx,y-cy)>tolerance_mm for x,y in centers):return PadstackInference(slot.id,None,("SLOT_PAD_CENTER_MISMATCH",))
    shapes={str(p.shape).upper() for p in selected}
    if len(shapes)!=1:return PadstackInference(slot.id,None,("SLOT_PAD_SHAPE_CONFLICT",))
    sx0,sy0=float(selected[0].size_x),float(selected[0].size_y)
    if any(not(_near(p.size_x,sx0,tolerance_mm) and _near(p.size_y,sy0,tolerance_mm)) for p in selected[1:]):
        return PadstackInference(slot.id,None,("SLOT_PAD_SIZE_CONFLICT",))
    nets={p.net_id for p in selected if p.net_id is not None}
    if len(nets)>1:return PadstackInference(slot.id,None,("SLOT_PAD_NET_CONFLICT",))
    net_id=next(iter(nets)) if nets else None
    pad_size=(sx0,sy0) if orth==0 else (sy0,sx0)
    layers=tuple(sorted((p.layer for p in selected),key=_layer_key))
    ps=PlatedSlotPadstack(slot.id,desc["center"],desc["angle_deg"],pad_size,str(selected[0].shape).upper(),(desc["long_mm"],desc["short_mm"]),layers,net_id,tuple(sorted(p.id for p in selected)),.95,("slot_plating_proven","multilayer_copper_coverage","uniform_pad_geometry"))
    return PadstackInference(slot.id,ps,())
