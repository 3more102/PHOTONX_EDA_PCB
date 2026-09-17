from .query import children,child
from .pads import read_pads
def read_footprints(root):
    out=[]
    for f in children(root,'footprint'):
        at=child(f,'at'); layer=child(f,'layer')
        out.append({'name':str(f[1]) if len(f)>1 else '', 'at':(float(at[1]),float(at[2])) if at else (0,0), 'layer':str(layer[1]) if layer else None,'pads':read_pads(f)})
    return out
