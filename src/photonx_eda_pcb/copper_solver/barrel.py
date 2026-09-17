def barrel_layers(drill,ordered_layers):
    names=[getattr(x,'name',str(x)) for x in ordered_layers]
    span=getattr(drill,'layer_span',None)
    if not span:return names if getattr(drill,'span_proven',False) else []
    start,end=span
    if start not in names or end not in names:return []
    a,b=names.index(start),names.index(end)
    if a>b:a,b=b,a
    return names[a:b+1]

def barrel_is_electrical(drill):return getattr(drill,'plating',None)=='plated' and bool(getattr(drill,'span_proven',False))
