def peripheral_coverage(pmap,component_ids):
    allc=set(map(str,component_ids));mapped={x.component_id for x in pmap.bindings}
    return 1.0 if not allc else round(len(allc&mapped)/len(allc),6)
def protocol_counts(pmap):
    out={}
    for x in pmap.bindings:out[x.protocol]=out.get(x.protocol,0)+1
    return dict(sorted(out.items()))
