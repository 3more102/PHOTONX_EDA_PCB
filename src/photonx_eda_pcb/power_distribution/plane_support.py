def plane_support_score(net_id,plane_areas):
    area=float(plane_areas.get(net_id,0.0))
    total=sum(max(0.0,float(v)) for v in plane_areas.values())
    return 0.0 if total<=0 else round(max(0.0,area)/total,6)
