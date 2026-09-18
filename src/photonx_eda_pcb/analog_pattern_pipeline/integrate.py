def add_analog_evidence(database,analysis):
    for r in analysis.evidence_records:database.upsert(r)
    return [r.id for r in analysis.evidence_records]
def add_analog_review(queue,analysis):
    existing={x.id for x in queue.items};added=[]
    for item in analysis.review_items:
        if item.id not in existing:queue.items.append(item);existing.add(item.id);added.append(item.id)
    return added
