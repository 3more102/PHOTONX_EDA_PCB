from .model import ViaSpanCandidate
from .candidates import pads_near_drill,pads_near_drill_bruteforce,build_pad_candidate_index
from .evidence import span_evidence


def _ordered_unique_layers(pads,copper):
    seen=[]
    for p in pads:
        layer=getattr(p,"layer",None)
        if layer in copper and layer not in seen:
            seen.append(layer)
    return sorted(seen,key=copper.index)


def _explicit_span(drill,copper):
    raw=getattr(drill,"layer_span",None)
    if raw is None:
        return None,None
    if not isinstance(raw,(tuple,list)) or len(raw)!=2:
        return None,"malformed"
    start,end=raw
    if start not in copper or end not in copper:
        return None,"unknown-layer"
    a,b=copper.index(start),copper.index(end)
    if a<=b:
        return (start,end),None
    return (end,start),None


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

        observed=_ordered_unique_layers(pads,copper)
        evidence=span_evidence(d,pads)
        explicit,span_error=_explicit_span(d,copper)
        raw_span=getattr(d,"layer_span",None)

        if raw_span is not None:
            if explicit is None:
                a=b=None;proven=False;conf=0.1
                evidence.append(f"explicit layer span rejected: {span_error}")
            else:
                a,b=explicit
                lo,hi=copper.index(a),copper.index(b)
                outside=[layer for layer in observed if not lo<=copper.index(layer)<=hi]
                span_proven=bool(getattr(d,"span_proven",False))
                plated=getattr(d,"plating","unknown")=="plated"
                if outside:
                    proven=False;conf=0.2
                    evidence.append("explicit layer span conflicts with observed pad layer(s): "+", ".join(outside))
                else:
                    proven=span_proven and plated
                    if proven:
                        conf=0.99
                    elif span_proven:
                        conf=0.75
                    else:
                        conf=0.7
        elif len(observed)>=2:
            a,b=observed[0],observed[-1]
            proven=False
            plating=getattr(d,"plating","unknown")
            conf=0.65 if plating=="plated" else (0.5 if plating=="unknown" else 0.25)
            evidence.append("observed multi-layer pad overlap is span hypothesis only")
        elif len(observed)==1:
            a=b=observed[0];proven=False;conf=0.35
        else:
            a=b=None;proven=False;conf=0.1

        out.append(ViaSpanCandidate(d.id,a,b,conf,evidence,proven))
    return out
