def analog_summary(blocks):
    kinds={}
    for b in blocks:kinds[b.kind]=kinds.get(b.kind,0)+1
    return {"total":len(blocks),"kinds":dict(sorted(kinds.items())),"low_confidence":sum(b.confidence<.7 for b in blocks)}
