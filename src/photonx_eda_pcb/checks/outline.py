from .base import CheckIssue
from ..geometry.distance import distance
def check_outline(board,tolerance:float=0.05):
    if not board.outline:return [CheckIssue("warning","OUTLINE_MISSING","no board outline reconstructed")]
    issues=[]
    for a,b in zip(board.outline,board.outline[1:]):
        if distance(a.end,b.start)>tolerance: issues.append(CheckIssue("warning","OUTLINE_GAP",f"gap between {a.id} and {b.id}",a.id))
    if distance(board.outline[-1].end,board.outline[0].start)>tolerance: issues.append(CheckIssue("warning","OUTLINE_OPEN","outline does not close",board.outline[-1].id))
    return issues
