from .model import ViaSpanCandidate
from .candidates import pads_near_drill,pads_near_drill_bruteforce,build_pad_candidate_index
from .evidence import span_evidence

def resolve_via_spans(board,stackup,tolerance_mm=0.15,*,use_spatial_index=True,cell_size_mm=None):
    copper=[x.name for x in stackup.copper_layers()];out=[]
    index=pad_by_id=None
    if use_spatial_index and board.pads:
        index,pad_by_id=build_pad_candidate_index(board,tolerance_mm,cell_size_mm)
    for d in board.drills:
        if use_spatial_index:
            pads=pads_near_drill(board,d,tolerance_mm,index=index,pad_by_id=pad_by_id)
        else:
            pads=pads_near_drill_bruteforce(board,d,tolerance_mm)
        layers=[p.layer for p in pads if p.layer in copper]
        uniq=[]
        for x in layers:
            if x not in uniq:uniq.append(x)
        if len(uniq)>=2:
            uniq=sorted(uniq,key=copper.index);a,b=uniq[0],uniq[-1]
            proven=d.plating=="plated";conf=0.95 if proven else 0.7
        elif len(uniq)==1:
            a=b=uniq[0];proven=False;conf=0.35
        else:
            a=b=None;proven=False;conf=0.1
        out.append(ViaSpanCandidate(d.id,a,b,conf,span_evidence(d,pads),proven))
    return out
