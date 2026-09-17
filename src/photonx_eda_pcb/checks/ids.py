from .base import CheckIssue
from ..core.collections import duplicates
def check_unique_object_ids(board):
    ids=[o.id for o in [*board.tracks,*board.pads,*board.drills,*board.outline]]
    return [CheckIssue("error","DUPLICATE_OBJECT_ID",f"duplicate object id {x}",x) for x in duplicates(ids)]
