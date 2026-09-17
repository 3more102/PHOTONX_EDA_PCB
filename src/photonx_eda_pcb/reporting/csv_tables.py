import csv,io
def nets_csv(board)->str:
    out=io.StringIO(); w=csv.writer(out); w.writerow(["net_id","label","confidence","member_count"])
    for n in board.nets:w.writerow([n.id,n.label or "",n.confidence,len(n.members)])
    return out.getvalue()
def components_csv(board)->str:
    out=io.StringIO(); w=csv.writer(out); w.writerow(["component_id","kind","confidence","pad_count"])
    for c in board.components:w.writerow([c.id,c.kind,c.confidence,len(c.pad_ids)])
    return out.getvalue()
