from collections import Counter
from .base import RuleIssue
def unique_object_ids(board):
    objs=[*getattr(board,'tracks',[]),*getattr(board,'pads',[]),*getattr(board,'drills',[]),*getattr(board,'outline',[])]
    counts=Counter(getattr(o,'id',None) for o in objs)
    return [RuleIssue('error','DUPLICATE_ID',f'duplicate object id {k}',k) for k,v in counts.items() if k is not None and v>1]
