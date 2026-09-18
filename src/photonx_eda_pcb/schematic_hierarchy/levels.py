def hierarchy_levels(result):
    priority={"power":0,"compute":1,"logic":2,"io":3}
    return sorted(result.blocks,key=lambda b:(priority.get(b.name,9),b.id))
