from collections import Counter
from .base import RuleIssue
from ..core.board_objects import iter_physical_objects

def unique_object_ids(board):
    counts=Counter(getattr(o,'id',None) for o in iter_physical_objects(board))
    return [RuleIssue('error','DUPLICATE_ID',f'duplicate object id {k}',k) for k,v in counts.items() if k is not None and v>1]
