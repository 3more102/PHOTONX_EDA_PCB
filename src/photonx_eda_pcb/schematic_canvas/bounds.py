from .geometry import object_bbox
def page_bounds(doc,page_id,padding=5.0):
    p=doc.pages[str(page_id)];objs=[]
    for oid in p.symbol_ids+p.wire_ids+p.label_ids+p.bus_ids:
        for t in (doc.symbols,doc.wires,doc.labels,doc.buses):
            if oid in t:objs.append(t[oid]);break
    if not objs:return (0,0,0,0)
    boxes=[object_bbox(x) for x in objs];pad=float(padding)
    return (min(b[0] for b in boxes)-pad,min(b[1] for b in boxes)-pad,max(b[2] for b in boxes)+pad,max(b[3] for b in boxes)+pad)
