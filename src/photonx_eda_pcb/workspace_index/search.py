def search_index(index,*,text="",role=None,tags=()):
    q=str(text).lower();want=set(map(str,tags));out=[]
    for a in index.artifacts:
        if role is not None and a.role!=role:continue
        if q and q not in a.path.lower() and q not in a.role.lower() and not any(q in t.lower() for t in a.tags):continue
        if want and not want.issubset(set(a.tags)):continue
        out.append(a)
    return out
