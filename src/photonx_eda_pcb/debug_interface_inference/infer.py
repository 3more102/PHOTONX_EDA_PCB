from .model import DebugInterfaceCandidate
from .labels import debug_signal,SWD,JTAG
def infer_debug_interfaces(labels,schematic_graph):
    by={"SWD":[],"JTAG":[]};resets=[]
    for net_id,label in labels.items():
        x=debug_signal(label)
        if x is None:continue
        proto,role=x
        if proto in by:by[proto].append((str(net_id),role))
        else:resets.append(str(net_id))
    out=[]
    for proto,items in by.items():
        roles={r for _,r in items}
        needed=SWD if proto=="SWD" else JTAG
        if not roles:continue
        nets=tuple(sorted(n for n,_ in items));comps=sorted({cid for cid,_,nid in schematic_graph.pin_edges if nid in nets})
        coverage=len(roles&needed)/len(needed)
        score=.45+.4*coverage+(.1 if len(comps)>=1 else 0)
        ev=["debug_labels",f"signal_coverage={coverage:.2f}"]
        if resets:ev.append("reset_signal_present")
        out.append(DebugInterfaceCandidate(proto,nets,tuple(comps),round(min(score,1),6),tuple(ev)))
    return sorted(out,key=lambda x:(-x.confidence,x.protocol))
