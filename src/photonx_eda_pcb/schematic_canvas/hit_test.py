from .geometry import object_bbox,bbox_contains
def hit_test(doc,page_id,x,y,tolerance=1.0):
    p=doc.pages[str(page_id)];ids=p.symbol_ids+p.label_ids+p.wire_ids+p.bus_ids;hits=[]
    tables=(doc.symbols,doc.labels,doc.wires,doc.buses)
    for oid in ids:
        obj=next((t[oid] for t in tables if oid in t),None)
        if obj is not None and bbox_contains(object_bbox(obj),float(x),float(y),tolerance):hits.append(oid)
    return tuple(hits)
