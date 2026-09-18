def hierarchy_report(result):
    return {"blocks":[{"id":b.id,"name":b.name,"components":list(b.component_ids),"nets":list(b.net_ids),"confidence":b.confidence,"evidence":list(b.evidence)} for b in result.blocks],"unassigned":list(result.unassigned_components)}
