from photonx_eda_pcb.review_workflow.model import ReviewItem
def engineering_review_items(*,thermal=(),yield_risk=None,pinmap_reports=()):
    out=[]
    for x in thermal:
        if x.risk>=.45:
            out.append(ReviewItem(f"thermal:{x.object_id}","thermal_risk",x.object_id,int(50+x.risk*40)))
    if yield_risk is not None and yield_risk.score>=.35:
        out.append(ReviewItem("yield:board","fabrication_yield","board",int(50+yield_risk.score*40)))
    for r in pinmap_reports:
        if r.issues:out.append(ReviewItem(f"pinmap:{r.component_id}","pinmap_conflict",r.component_id,80))
    return sorted(out,key=lambda x:(-x.priority,x.id))
