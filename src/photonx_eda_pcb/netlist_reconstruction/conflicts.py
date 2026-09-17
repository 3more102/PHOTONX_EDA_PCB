def label_conflicts(candidates):
    out=[]
    for net_id,items in candidates.items():
        labels={x.get('label') for x in items if x.get('label')}
        if len(labels)>1:out.append({'net_id':net_id,'labels':sorted(labels)})
    return out
