def objects_in_page(doc,page_id):
    p=doc.pages[str(page_id)]
    return tuple(p.symbol_ids+p.wire_ids+p.label_ids+p.bus_ids)
def selected_objects(doc,ids):
    out=[]
    for oid in ids:
        for table in (doc.symbols,doc.wires,doc.labels,doc.buses):
            if oid in table:out.append(table[oid]);break
    return out
