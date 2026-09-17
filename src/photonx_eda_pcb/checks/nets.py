from .base import CheckIssue
def check_nets(board):
    issues=[]; objects=board.object_index(); seen={}
    for net in board.nets:
        if not 0<=net.confidence<=1: issues.append(CheckIssue("error","NET_CONFIDENCE_INVALID","net confidence outside [0,1]",net.id))
        for member in net.members:
            if member not in objects:
                issues.append(CheckIssue("error","NET_MEMBER_MISSING",f"unknown member {member}",net.id)); continue
            if member in seen and seen[member]!=net.id: issues.append(CheckIssue("error","NET_MEMBER_MULTIPLE",f"member {member} appears in multiple nets",member))
            seen[member]=net.id
    return issues
