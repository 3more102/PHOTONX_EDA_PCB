from .model import DrcIssue
from ..core.board_objects import iter_physical_objects

def check_duplicate_ids(board,cfg):
    objs=iter_physical_objects(board); seen=set(); out=[]
    for o in objs:
        if o.id in seen:out.append(DrcIssue('error','DUPLICATE_ID','duplicate physical object id',(o.id,)))
        seen.add(o.id)
    return out
