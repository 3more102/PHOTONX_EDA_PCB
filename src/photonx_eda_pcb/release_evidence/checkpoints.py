def reviews_closed(checkpoints):
    items=list(checkpoints)
    return bool(items) and all(getattr(x,"closed",False) for x in items)
