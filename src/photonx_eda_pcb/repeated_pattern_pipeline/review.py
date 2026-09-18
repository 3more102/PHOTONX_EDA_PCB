def add_analysis_review(queue,analysis):
    existing={x.id for x in queue.items};added=[]
    for item in analysis.review_items:
        if item.id not in existing:
            queue.items.append(item);existing.add(item.id);added.append(item.id)
    return added
