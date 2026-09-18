def rc_pairs(components,schematic_graph):
    by_net={}
    for c in components:
        cid=str(getattr(c,"id",""));kind=str(getattr(c,"kind","")).lower()
        nets={nid for x,_,nid in schematic_graph.pin_edges if x==cid}
        for n in nets:by_net.setdefault(n,[]).append((cid,kind))
    out=[]
    for n,items in by_net.items():
        rs=[i for i in items if "resistor" in i[1]];cs=[i for i in items if "capacitor" in i[1]]
        for r in rs:
            for c in cs:out.append((r[0],c[0],n))
    return sorted(out)
