from photonx_eda_pcb.review_workflow.model import ReviewItem
SENSITIVE={"merge_nets","split_net","assign_reference","set_component_kind"}
def review_items_for_edits(state):
    return [ReviewItem("edit:"+x.id,"manual_edit",x.object_id,85 if x.kind in SENSITIVE else 40) for x in state.pending if x.kind in SENSITIVE]
