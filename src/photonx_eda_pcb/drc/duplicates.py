from .model import DrcIssue
def check_duplicate_ids(board,cfg):
    objs=[*board.tracks,*board.pads,*board.drills,*board.outline]; seen=set(); out=[]
    for o in objs:
        if o.id in seen:out.append(DrcIssue('error','DUPLICATE_ID','duplicate physical object id',(o.id,)))
        seen.add(o.id)
    return out
