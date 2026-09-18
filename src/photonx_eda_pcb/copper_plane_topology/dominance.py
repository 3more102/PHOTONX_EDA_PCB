def dominant_net(topology):
    from .net_areas import net_areas
    a=net_areas(topology)
    return None if not a else max(sorted(a),key=lambda k:a[k])
