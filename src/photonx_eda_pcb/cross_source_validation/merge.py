def merge_observations(items):
    grouped={}
    for o in items:grouped.setdefault((o.subject_id,o.field),[]).append(o)
    out={}
    for key,obs in grouped.items():
        best=max(obs,key=lambda x:(x.confidence,x.source))
        out[key]={'value':best.value,'source':best.source,'confidence':best.confidence}
    return out
