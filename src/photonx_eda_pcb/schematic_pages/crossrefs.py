def cross_page_nets(page_set):
    owners={}
    for p in page_set.pages:
        for n in p.nets:owners.setdefault(n,[]).append(p.id)
    return {n:tuple(sorted(ids)) for n,ids in owners.items() if len(ids)>1}
