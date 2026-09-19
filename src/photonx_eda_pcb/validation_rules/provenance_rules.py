from .base import RuleIssue

def source_references_present(board):
    out=[]
    objects=[
        *getattr(board,'tracks',[]),
        *getattr(board,'pads',[]),
        *getattr(board,'drills',[]),
        *getattr(board,'outline',[]),
        *getattr(board,'slots',[]),
        *getattr(board,'routes',[]),
        *getattr(board,'regions',[]),
    ]
    for o in objects:
        prov=getattr(o,'provenance',None)
        if prov is not None and not getattr(prov,'sources',[]): out.append(RuleIssue('info','SOURCE_REF_MISSING','no source reference recorded',o.id))
    return out
