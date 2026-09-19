from collections import Counter
from .base import CheckIssue
def check_components(board):
    issues=[]; pads={p.id for p in board.pads}
    component_id_counts=Counter(c.id for c in board.components)
    for component_id,count in sorted(component_id_counts.items()):
        if count>1: issues.append(CheckIssue("error","DUPLICATE_COMPONENT_ID",f"duplicate component hypothesis id {component_id}",component_id))
    for c in board.components:
        duplicate_pad_ids=sorted(pid for pid,count in Counter(c.pad_ids).items() if count>1)
        if duplicate_pad_ids: issues.append(CheckIssue("error","COMPONENT_PAD_DUPLICATE",f"duplicate pad ids {duplicate_pad_ids}",c.id))
        if not 0<=c.confidence<=1: issues.append(CheckIssue("error","COMPONENT_CONFIDENCE_INVALID","component confidence outside [0,1]",c.id))
        for pid in c.pad_ids:
            if pid not in pads: issues.append(CheckIssue("error","COMPONENT_PAD_MISSING",f"unknown pad {pid}",c.id))
        if not c.pad_ids: issues.append(CheckIssue("warning","COMPONENT_NO_PADS","component hypothesis has no pads",c.id))
    return issues
