def add_annotation(store,annotation):
    if any(x.id==annotation.id for x in store.items):raise ValueError("duplicate annotation id")
    store.items.append(annotation);return store
def remove_annotation(store,annotation_id):
    before=len(store.items);store.items=[x for x in store.items if x.id!=annotation_id];return before-len(store.items)
