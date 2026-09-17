from .base import CheckIssue
def check_components(board):
    issues=[]; pads={p.id for p in board.pads}
    for c in board.components:
        if not 0<=c.confidence<=1: issues.append(CheckIssue("error","COMPONENT_CONFIDENCE_INVALID","component confidence outside [0,1]",c.id))
        for pid in c.pad_ids:
            if pid not in pads: issues.append(CheckIssue("error","COMPONENT_PAD_MISSING",f"unknown pad {pid}",c.id))
        if not c.pad_ids: issues.append(CheckIssue("warning","COMPONENT_NO_PADS","component hypothesis has no pads",c.id))
    return issues
