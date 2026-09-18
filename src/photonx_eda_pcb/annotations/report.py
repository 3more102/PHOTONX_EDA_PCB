def annotation_summary(store):
    return {"count":len(store.items),"resolved":sum(x.resolved for x in store.items),"unresolved":sum(not x.resolved for x in store.items)}
