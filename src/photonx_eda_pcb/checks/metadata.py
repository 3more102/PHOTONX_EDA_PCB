from .base import CheckIssue
def check_metadata(board):
    issues=[]
    if "units" in board.metadata and board.metadata["units"] not in {"mm","inch"}: issues.append(CheckIssue("warning","METADATA_UNITS_UNKNOWN","metadata units should be mm or inch"))
    return issues
