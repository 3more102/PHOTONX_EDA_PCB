from .query import children,child
def read_vias(root):
    out=[]
    for v in children(root,'via'):
        at=child(v,'at'); size=child(v,'size'); drill=child(v,'drill'); layers=child(v,'layers'); net=child(v,'net')
        out.append({'at':(float(at[1]),float(at[2])),'size':float(size[1]),'drill':float(drill[1]),'layers':tuple(map(str,layers[1:])), 'net':int(net[1]) if net else None})
    return out
