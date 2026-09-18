from photonx_eda_pcb.review_workflow.model import ReviewItem
SENSITIVE={"assign_reference","rename_net","set_library_id","delete_symbol"}
def review_for_edit(kind,object_id,confidence=1.0):
    if kind not in SENSITIVE and confidence>=.6:return None
    priority=80 if kind in SENSITIVE else int(50+(1-float(confidence))*30)
    return ReviewItem(f"schematic:{kind}:{object_id}","schematic_edit",str(object_id),priority)
