from .model import ConditioningStage
from .rc import rc_pairs
from .ferrites import ferrite_components
def infer_conditioning_stages(components,schematic_graph,signal_roles=None):
    signal_roles=signal_roles or {};out=[]
    for r,c,n in rc_pairs(components,schematic_graph):
        roles=signal_roles.get(n,())
        conf=.65+(.1 if roles else 0)
        out.append(ConditioningStage(f"rc:{r}:{c}:{n}","rc_filter",(r,c),(n,),round(conf,12),("shared_net","resistor_capacitor")))
    for cid in ferrite_components(components):
        nets=tuple(sorted({nid for x,_,nid in schematic_graph.pin_edges if x==cid}))
        if nets:out.append(ConditioningStage("ferrite:"+cid,"ferrite_filter",(cid,),nets,.7,("component_identity",)))
    return sorted(out,key=lambda x:(x.kind,x.id))
