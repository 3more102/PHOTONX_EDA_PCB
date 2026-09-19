from .base import RuleIssue
from ..core.board_objects import iter_physical_objects

def source_references_present(board):
    out=[]
    for o in iter_physical_objects(board):
        prov=getattr(o,'provenance',None)
        if prov is not None and not getattr(prov,'sources',[]): out.append(RuleIssue('info','SOURCE_REF_MISSING','no source reference recorded',o.id))
    return out
