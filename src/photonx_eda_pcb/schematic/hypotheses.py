from .netlist import component_net_map
from .symbols import symbol_hints

def infer_schematic_hypotheses(board,footprints=None):
    fmap={f.id:f for f in (footprints or [])}; nets=component_net_map(board); out=[]
    for c in board.components:
        kind=c.kind; hints=symbol_hints(kind)
        out.append({'component_id':c.id,'pins':nets.get(c.id,[]),'symbol_hints':hints,'confidence':c.confidence*0.8,'status':'hypothesis'})
    return out
