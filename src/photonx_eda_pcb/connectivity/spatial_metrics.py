from .geometry import copper_shape
from .spatial import layer_candidate_pairs

def connectivity_candidate_metrics(board,tolerance_mm=.03,cell_size_mm=None):
    objects=[*board.tracks,*board.pads];shapes={o.id:copper_shape(o) for o in objects}
    total=0
    by_layer={}
    for o in objects:by_layer[o.layer]=by_layer.get(o.layer,0)+1
    for n in by_layer.values():total+=n*(n-1)//2
    pairs=layer_candidate_pairs(objects,shapes,tolerance_mm,cell_size_mm)
    return {"objects":len(objects),"same_layer_bruteforce_pairs":total,"spatial_candidate_pairs":len(pairs),"reduction_ratio":1.0 if total==0 else round(1-len(pairs)/total,6)}
