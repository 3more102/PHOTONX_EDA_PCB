from .base import CheckIssue
from ..core.board_objects import iter_physical_objects
from ..core.collections import duplicates

def check_unique_object_ids(board):
    ids=[o.id for o in iter_physical_objects(board)]
    return [CheckIssue("error","DUPLICATE_OBJECT_ID",f"duplicate object id {x}",x) for x in duplicates(ids)]
