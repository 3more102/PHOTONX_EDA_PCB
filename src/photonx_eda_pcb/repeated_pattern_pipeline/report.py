from .summary import analysis_summary
def analysis_report(a):
    return {"summary":analysis_summary(a),"groups":[{"id":g.id,"instances":len(g.instances),"similarity":g.similarity,"confidence":g.confidence} for g in a.repeated_groups],"channels":[{"id":c.id,"kind":c.kind,"confidence":c.confidence} for c in a.channels],"patterns":[{"pattern":p.pattern,"object_id":p.object_id,"score":p.score} for p in a.pattern_matches]}
