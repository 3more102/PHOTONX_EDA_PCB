from .metrics import bounds
def classify_cutouts(loops):
    if not loops:return []
    areas=[]
    for l in loops:
        x0,y0,x1,y1=bounds(l);areas.append(((x1-x0)*(y1-y0),l))
    outer=max(areas,key=lambda x:x[0])[1]
    return [(l.id,l.id!=outer.id) for _,l in areas]
