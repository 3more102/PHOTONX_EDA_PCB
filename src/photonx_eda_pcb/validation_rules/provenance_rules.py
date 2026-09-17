from .base import RuleIssue
def source_references_present(board):
    out=[]
    for o in [*getattr(board,'tracks',[]),*getattr(board,'pads',[]),*getattr(board,'drills',[]),*getattr(board,'outline',[])]:
        prov=getattr(o,'provenance',None)
        if prov is not None and not getattr(prov,'sources',[]): out.append(RuleIssue('info','SOURCE_REF_MISSING','no source reference recorded',o.id))
    return out
