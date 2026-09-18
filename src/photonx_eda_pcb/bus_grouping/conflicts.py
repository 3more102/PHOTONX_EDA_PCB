def overlapping_buses(candidates):
    out=[]
    for i,a in enumerate(candidates):
        sa=set(a.net_ids)
        for b in candidates[i+1:]:
            overlap=sorted(sa&set(b.net_ids))
            if overlap:out.append((a.name,b.name,tuple(overlap)))
    return out
