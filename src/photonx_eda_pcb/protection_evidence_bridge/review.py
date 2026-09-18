from photonx_eda_pcb.review_workflow.model import ReviewItem
def protection_review_items(candidates=(),unprotected_connectors=()):
    out=[ReviewItem("protection:"+x.component_id,"protection_hypothesis",x.component_id,55) for x in candidates if x.confidence<.75]
    out += [ReviewItem("unprotected:"+str(c),"unprotected_external_interface",str(c),75) for c in unprotected_connectors]
    return sorted(out,key=lambda x:(-x.priority,x.id))
