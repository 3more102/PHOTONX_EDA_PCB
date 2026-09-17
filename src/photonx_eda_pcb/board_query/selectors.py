def _objects(board):
    names=("tracks","pads","drills","components")
    result=[]
    for name in names: result.extend(getattr(board,name,[]) or [])
    return result
def select_by_layer(board,layer): return [obj for obj in _objects(board) if getattr(obj,"layer",None)==layer]
def select_by_net(board,net_id): return [obj for obj in _objects(board) if getattr(obj,"net_id",None)==net_id]
def select_by_kind(board,kind): return [obj for obj in _objects(board) if obj.__class__.__name__.lower()==str(kind).lower()]
