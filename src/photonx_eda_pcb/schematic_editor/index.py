def component_symbol_index(doc):return {s.component_id:s.id for s in sorted(doc.symbols.values(),key=lambda x:(x.component_id,x.id))}
def net_objects(doc):
    out={}
    for w in doc.wires.values():out.setdefault(w.net_id,[]).append(w.id)
    for l in doc.labels.values():out.setdefault(l.net_id,[]).append(l.id)
    for b in doc.buses.values():
        for n in b.net_ids:out.setdefault(n,[]).append(b.id)
    return {k:tuple(sorted(v)) for k,v in sorted(out.items())}
