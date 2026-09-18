def net_areas(topology):
    out={}
    for i in topology.islands:
        if i.net_id is not None:out[i.net_id]=out.get(i.net_id,0.0)+float(i.area_mm2)
    return out
