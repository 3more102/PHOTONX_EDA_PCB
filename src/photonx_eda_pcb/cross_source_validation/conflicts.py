def find_conflicts(items):
    grouped={}
    for o in items:grouped.setdefault((o.subject_id,o.field),[]).append(o)
    out=[]
    for key,obs in grouped.items():
        vals={repr(o.value) for o in obs}
        if len(vals)>1:out.append({'subject_id':key[0],'field':key[1],'sources':sorted(o.source for o in obs),'values':sorted(vals)})
    return out
