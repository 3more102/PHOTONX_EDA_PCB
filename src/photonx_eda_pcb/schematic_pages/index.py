def component_page_index(page_set):
    out={}
    for p in page_set.pages:
        for c in p.components:out.setdefault(c,[]).append(p.id)
    return {k:tuple(v) for k,v in sorted(out.items())}
