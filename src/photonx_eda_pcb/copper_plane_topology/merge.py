def merge_same_net_contacts(topology):
    groups={}
    by_id={i.id:i for i in topology.islands}
    for a,neighbors in topology.adjacency.items():
        for b in neighbors:
            ia,ib=by_id.get(a),by_id.get(b)
            if ia and ib and ia.net_id is not None and ia.net_id==ib.net_id:
                groups.setdefault(ia.net_id,set()).update((a,b))
    return {k:tuple(sorted(v)) for k,v in groups.items()}
