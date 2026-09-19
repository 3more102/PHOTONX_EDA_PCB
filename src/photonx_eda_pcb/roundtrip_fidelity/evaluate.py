from .model import FidelitySection,FidelityReport
DEFAULT_WEIGHTS={"tracks":2.0,"pads":2.0,"drills":2.0,"nets":3.0,"components":2.0,"outline":2.0,"mechanical_slots":2.0,"regions":2.0}
def evaluate_fidelity(left,right,compare_fn=None,weights=None):
    from photonx_eda_pcb.roundtrip.compare import compare_board_models
    compare_fn=compare_fn or compare_board_models;weights={**DEFAULT_WEIGHTS,**(weights or {})}
    diffs=compare_fn(left,right);by={d["section"]:d for d in diffs}
    sections=[]
    names=sorted(set(DEFAULT_WEIGHTS)|set(by))
    for name in names:
        d=by.get(name)
        if d:sections.append(FidelitySection(name,False,int(d.get("left_count",0)),int(d.get("right_count",0)),float(weights.get(name,1))))
        else:sections.append(FidelitySection(name,True,0,0,float(weights.get(name,1))))
    total=sum(x.weight for x in sections);good=sum(x.weight for x in sections if x.equal)
    return FidelityReport(sections,1.0 if total==0 else round(good/total,6),all(x.equal for x in sections))
