from .model import CheckpointDecision
VALID={"approved","rejected","needs_work"}
def add_decision(checkpoint,reviewer,decision,note=""):
    if decision not in VALID:raise ValueError("invalid decision")
    checkpoint.decisions.append(CheckpointDecision(str(reviewer),str(decision),str(note)));return checkpoint
def close_if_approved(checkpoint,min_approvals=1):
    approvals=sum(d.decision=="approved" for d in checkpoint.decisions)
    blockers=any(d.decision=="rejected" for d in checkpoint.decisions)
    checkpoint.closed=approvals>=int(min_approvals) and not blockers
    return checkpoint.closed
