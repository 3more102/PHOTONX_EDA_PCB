from .query import children,child
def read_pads(footprint):
    out=[]
    for p in children(footprint,'pad'):
        at=child(p,'at'); size=child(p,'size'); drill=child(p,'drill'); layers=child(p,'layers'); net=child(p,'net')
        out.append({'number':str(p[1]),'kind':str(p[2]),'shape':str(p[3]),'at':(float(at[1]),float(at[2])) if at else (0.0,0.0),'size':(float(size[1]),float(size[2])) if size else None,'drill':float(drill[1]) if drill else None,'layers':tuple(map(str,layers[1:])) if layers else (), 'net':int(net[1]) if net else None})
    return out
