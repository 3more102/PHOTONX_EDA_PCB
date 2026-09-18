def compare_variants(a,b):
    refs=sorted(set(a.components)|set(b.components));out=[]
    for r in refs:
        x=a.components.get(r);y=b.components.get(r)
        if x!=y:out.append({"reference":r,"a":x,"b":y})
    return out
