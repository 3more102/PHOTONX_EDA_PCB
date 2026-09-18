from .base import CheckIssue
def check_drills(board):
    issues=[];allowed={"unknown","plated","non_plated","non-plated"}
    for d in board.drills:
        if d.plating not in allowed:issues.append(CheckIssue("warning","DRILL_PLATING_UNKNOWN_ENUM",f"unexpected plating value {d.plating}",d.id))
    for s in getattr(board,"slots",()):
        if s.plated not in allowed:issues.append(CheckIssue("warning","SLOT_PLATING_UNKNOWN_ENUM",f"unexpected slot plating value {s.plated}",s.id))
    return issues
