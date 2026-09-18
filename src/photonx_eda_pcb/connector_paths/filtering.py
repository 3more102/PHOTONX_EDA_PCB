def shortest_per_connector(paths):
    best={}
    for p in paths:
        if p.connector_id not in best or p.hops<best[p.connector_id].hops:best[p.connector_id]=p
    return [best[k] for k in sorted(best)]
