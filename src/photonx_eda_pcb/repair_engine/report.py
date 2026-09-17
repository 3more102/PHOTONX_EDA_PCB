from collections import Counter
def repair_report(candidates):
    return {'total':len(candidates),'by_kind':dict(Counter(x.kind for x in candidates)),'automatic_candidates':sum(x.automatic for x in candidates),'mean_confidence':(sum(x.confidence for x in candidates)/len(candidates) if candidates else 0.0)}
