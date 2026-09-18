from photonx_eda_pcb.review_workflow.model import ReviewItem
def review_items(groups,ambiguity_threshold=.85):
    out=[]
    for g in groups:
        if g.confidence<float(ambiguity_threshold) or any(i.differences for i in g.instances):
            out.append(ReviewItem("review:"+g.id,"repeated_circuit",g.id,60))
    return out
