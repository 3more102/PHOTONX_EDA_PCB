from photonx_eda_pcb.analog_blocks.summary import analog_summary
def analog_analysis_report(a):return {"summary":analog_summary(a.blocks),"blocks":[{"id":b.id,"kind":b.kind,"confidence":b.confidence,"components":list(b.components)} for b in a.blocks],"review_items":len(a.review_items)}
