from .base import CheckIssue
from ..core.board_objects import iter_physical_objects

def check_provenance(board):
    issues=[]
    for obj in iter_physical_objects(board):
        if not obj.provenance.sources: issues.append(CheckIssue("info","PROVENANCE_SOURCE_MISSING","object has no source reference",obj.id))
    return issues
