from .model import ErcIssue
def check_components(board):
    out=[]
    for c in board.components:
        if not c.pad_ids:out.append(ErcIssue('error','COMPONENT_NO_PINS','component hypothesis has no pads',c.id))
        if c.confidence<0.3:out.append(ErcIssue('info','COMPONENT_LOW_CONFIDENCE','component identity is highly uncertain',c.id))
    return out
