from .base import CheckIssue
def check_drills(board):
    issues=[]; allowed={"unknown","plated","non_plated"}
    for d in board.drills:
        if d.plating not in allowed: issues.append(CheckIssue("warning","DRILL_PLATING_UNKNOWN_ENUM",f"unexpected plating value {d.plating}",d.id))
    return issues
