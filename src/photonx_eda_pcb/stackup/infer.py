from .model import LayerSpec, StackupModel
from .layer_roles import role_for_layer,is_copper

def infer_stackup(board)->StackupModel:
    names=[]
    for obj in [*board.tracks,*board.pads,*getattr(board,"regions",())]:
        if getattr(obj,'layer',None) and obj.layer not in names:names.append(obj.layer)
    if board.outline and 'Edge.Cuts' not in names:names.append('Edge.Cuts')
    def key(n):
        if n=='F.Cu':return (0,n)
        if n.startswith('In') and n.endswith('.Cu'):
            try:return (1,int(n[2:-3]))
            except:return (1,999)
        if n=='B.Cu':return (2,n)
        return (3,n)
    names=sorted(names,key=key)
    layers=[LayerSpec(n,role_for_layer(n),i,is_copper(n)) for i,n in enumerate(names)]
    copper=sum(x.copper for x in layers)
    conf=0.9 if {'F.Cu','B.Cu'}<=set(names) else (0.65 if copper else 0.2)
    ev=[f'{copper} copper layer(s) observed from reconstructed objects']
    return StackupModel(layers,conf,ev)
