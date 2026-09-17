def apply_label_candidates(netlist,candidates):
    for net_id,items in candidates.items():
        ranked=sorted(items,key=lambda x:(-float(x.get('confidence',0)),str(x.get('label',''))))
        if ranked:netlist.labels[net_id]=ranked[0]['label']
    return netlist
