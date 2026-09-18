from .model import AssemblyComponent,AssemblyView
def build_assembly(placements,confidence_by_ref=None):
    confidence_by_ref=confidence_by_ref or {}
    comps=[]
    for p in placements:
        comps.append(AssemblyComponent(str(p.reference),(float(p.x),float(p.y)),float(p.rotation),str(p.side).lower(),str(p.footprint),str(p.value),float(confidence_by_ref.get(p.reference,1.0))))
    comps.sort(key=lambda c:(c.side,c.reference))
    return AssemblyView(comps,["pick_place"] if comps else [])
