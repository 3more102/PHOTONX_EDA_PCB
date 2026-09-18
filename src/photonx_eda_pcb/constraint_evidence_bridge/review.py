from photonx_eda_pcb.review_workflow.model import ReviewItem
def constraint_review_items(constraint_set,terminations=()):
    out=[]
    for c in constraint_set.constraints:
        if c.confidence<.6:out.append(ReviewItem("constraint:"+c.net_id,"constraint_candidate",c.net_id,55))
    for t in terminations:
        if t.confidence<.7:out.append(ReviewItem("termination:"+t.component_id,"termination_candidate",t.component_id,60))
    return sorted(out,key=lambda x:(-x.priority,x.id))
