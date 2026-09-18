from .prefix import prefix_for_kind
def assign_missing_references(components,used=()):
    used=set(map(str,used));counters={};out={}
    for c in sorted(components,key=lambda x:str(getattr(x,"id",""))):
        cid=str(getattr(c,"id",""));existing=getattr(c,"reference",None)
        if existing:used.add(str(existing));out[cid]=str(existing);continue
        prefix=prefix_for_kind(getattr(c,"kind","unknown"));n=counters.get(prefix,1)
        while f"{prefix}{n}" in used:n+=1
        ref=f"{prefix}{n}";used.add(ref);counters[prefix]=n+1;out[cid]=ref
    return out
