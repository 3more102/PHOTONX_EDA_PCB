from photonx_eda_pcb.review_workflow.model import ReviewItem
def connector_review_items(pin_functions=()):
    out=[]
    for x in pin_functions:
        if x.function is None:out.append(ReviewItem(f"connector:{x.connector_id}:{x.pin}","connector_pin_unresolved",f"{x.connector_id}:{x.pin}",60))
        elif x.conflicts:out.append(ReviewItem(f"connector:{x.connector_id}:{x.pin}:conflict","connector_pin_conflict",f"{x.connector_id}:{x.pin}",80))
    return sorted(out,key=lambda x:(-x.priority,x.id))
