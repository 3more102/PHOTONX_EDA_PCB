def mapping_conflicts(pmap):
    by={}
    for x in pmap.bindings:by.setdefault((x.component_id,x.protocol),[]).append(x)
    out=[]
    for key,items in by.items():
        roles={x.role for x in items};nets={x.nets for x in items}
        if len(roles)>1 or len(nets)>1:out.append((key,tuple(items)))
    return out
