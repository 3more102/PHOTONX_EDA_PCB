from ..models import BoardModel
from .completeness import completeness_score
def quality_score(board:BoardModel)->float:
    base=completeness_score(board)
    errors=sum(1 for d in board.diagnostics if d.severity.lower()=="error")
    warnings=sum(1 for d in board.diagnostics if d.severity.lower()=="warning")
    return max(0.0,min(1.0,base-0.08*errors-0.02*warnings))
