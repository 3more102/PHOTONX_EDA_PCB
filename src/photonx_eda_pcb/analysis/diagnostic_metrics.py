from collections import Counter
from ..models import BoardModel
def diagnostics_by_severity(board:BoardModel)->dict[str,int]: return dict(Counter(d.severity.lower() for d in board.diagnostics))
def diagnostics_by_code(board:BoardModel)->dict[str,int]: return dict(Counter(d.code for d in board.diagnostics))
