from photonx_eda_pcb.review_workflow.model import ReviewItem
def analog_review_items(blocks,threshold=.8):
    return [ReviewItem("review:"+b.id,"analog_block",b.id,int(50+(1-b.confidence)*30)) for b in blocks if b.confidence<float(threshold) or b.assumptions]
