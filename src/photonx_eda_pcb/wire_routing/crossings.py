from .segments import segments
def _cross(a,b):
    (a1,a2),(b1,b2)=a,b
    av=a1[0]==a2[0];bv=b1[0]==b2[0]
    if av==bv:return False
    v,h=(a,b) if av else (b,a);x=v[0][0];y=h[0][1]
    return min(v[0][1],v[1][1])<y<max(v[0][1],v[1][1]) and min(h[0][0],h[1][0])<x<max(h[0][0],h[1][0])
def count_crossings(routes):
    seg=[(r,s) for r in routes for s in segments(r)];count=0
    for i,(ra,a) in enumerate(seg):
        for rb,b in seg[i+1:]:
            if ra is rb:continue
            if _cross(a,b):count+=1
    return count
