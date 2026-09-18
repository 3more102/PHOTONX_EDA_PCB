def bridge_summary(records,review_items):
    kinds={}
    for r in records:kinds[r.kind]=kinds.get(r.kind,0)+1
    return {"evidence_records":len(records),"review_items":len(review_items),"kinds":dict(sorted(kinds.items()))}
