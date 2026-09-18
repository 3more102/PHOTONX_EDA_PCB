def checkpoint_coverage(c,completed_items):
    req=set(c.required_items)
    if not req:return 1.0
    return round(len(req&set(completed_items))/len(req),6)
