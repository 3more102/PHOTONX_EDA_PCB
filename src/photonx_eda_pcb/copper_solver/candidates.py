def bbox_candidates(objects,bbox_of,tolerance=0.0):
    items=[(getattr(o,'id',str(i)),bbox_of(o)) for i,o in enumerate(objects)]
    out=[]
    for i,(aid,a) in enumerate(items):
        for bid,b in items[i+1:]:
            if not (a[2]+tolerance<b[0] or b[2]+tolerance<a[0] or a[3]+tolerance<b[1] or b[3]+tolerance<a[1]):out.append((aid,bid))
    return out

def layer_partition(objects):
    out={}
    for o in objects:out.setdefault(getattr(o,'layer','unknown'),[]).append(o)
    return out
